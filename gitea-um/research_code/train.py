"""Portable version of the matched MPD encoder training loop; no private I/O."""
import argparse
import math
import numpy as np
import torch
import torch.nn.functional as F
from encoder import Net
from augment import augment_rgb
from protocol import check_people, evaluate


def margin_loss(z, weights, labels):
    c = (F.normalize(z) @ F.normalize(weights).T).clamp(-.99999, .99999)
    g = c.gather(1, labels[:, None])
    m = .5
    phi = torch.where(g > math.cos(math.pi - m),
                      g * math.cos(m) - (1 - g*g).sqrt() * math.sin(m),
                      g - math.sin(m) * m)
    return F.cross_entropy(64 * c.scatter(1, labels[:, None], phi), labels)


def tensor(x, device):
    return torch.from_numpy(np.ascontiguousarray(x)).permute(0, 3, 1, 2).to(device).float() / 127.5 - 1


def fit(data, epochs, device, mode, batch=32):
    x, y = data['train_rgb'], data['train_class']
    check_people(data['train_person'], data['val_person'], data['eval_person'])
    for name in ('train', 'val'):
        im = data[name+'_rgb']
        if im.dtype != np.uint8 or im.shape[1:] != (112,112,3) or not len(im):
            raise ValueError("Expected nonempty uint8 NHWC RGB crops at 112x112")
        if len(data[name+'_class']) != len(im) or len(data[name+'_person']) != len(im):
            raise ValueError("Image, person and class arrays must have matching lengths")
    roles = data['val_gallery']
    if roles.dtype != bool or roles.shape != (len(data['val_rgb']),) or not roles.any() or roles.all():
        raise ValueError("Expected validation gallery and probe roles")
    if len(x) < 2 or batch < 2 or epochs < 1:
        raise ValueError("Need at least two training examples and a positive epoch count")
    _, y = np.unique(y, return_inverse=True)
    torch.manual_seed(18011)
    net = Net().to(device)
    w = torch.nn.Parameter(torch.empty(int(y.max()) + 1, 512, device=device))
    torch.nn.init.xavier_uniform_(w)
    opt = torch.optim.SGD([*net.parameters(), w], lr=.025, momentum=.9, weight_decay=.0005)
    for ep in range(epochs):
        net.train()
        opt.param_groups[0]['lr'] = .025 * .1**(int(ep >= 7) + int(ep >= 15))
        for ix in torch.randperm(len(x)).split(batch):
            if len(ix) < 2:
                continue
            ids = ix.tolist()
            images = [augment_rgb(x[j], mode, np.random.default_rng(18011 + ep*100000 + j)) for j in ids]
            loss = margin_loss(net(tensor(np.stack(images), device)), w, torch.as_tensor(y[ids], device=device))
            if not torch.isfinite(loss):
                raise ArithmeticError("Non-finite loss")
            opt.zero_grad()
            loss.backward()
            opt.step()
        net.eval()
        with torch.inference_mode():
            v = np.concatenate([net(tensor(block, device)).cpu().numpy() for block in np.array_split(data['val_rgb'], (len(roles)+15)//16)])
        labels = data['val_class']
        print({'epoch': ep+1, 'validation': evaluate(zip(labels[roles],v[roles]), zip(labels[~roles],v[~roles]))})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--npz', help='Private pre-cropped data in the documented schema; omit for random synthetic smoke test')
    p.add_argument('--epochs', type=int)
    p.add_argument('--device', choices=['cpu','cuda'], default='cpu')
    p.add_argument('--mode', choices=['none','geometry'], default='none')
    a = p.parse_args()
    torch.set_num_threads(2)
    if a.npz:
        with np.load(a.npz, allow_pickle=False) as d:
            fit(d, 20 if a.epochs is None else a.epochs, a.device, a.mode)
    else:
        rng = np.random.default_rng(8)
        data = dict(train_rgb=rng.integers(256,size=(4,112,112,3),dtype=np.uint8),
                    val_rgb=rng.integers(256,size=(4,112,112,3),dtype=np.uint8),
                    train_class=np.array([0,1,0,1]),val_class=np.array([2,3,2,3]),
                    train_person=[0,1,0,1],val_person=[2,3,2,3],eval_person=[4],
                    val_gallery=np.array([True,True,False,False]))
        print('SYNTHETIC ONLY: no recognition-performance meaning')
        fit(data, 1 if a.epochs is None else a.epochs, a.device, a.mode)
