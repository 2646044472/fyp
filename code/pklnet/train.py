import argparse

import torch
import torch.nn as nn
import torch.nn.functional as F


import random
import numpy as np
import cv2
import os

import matplotlib.pyplot as plt
plt.switch_backend('agg')


from lib.utils.tools.configer import Configer

from torch.optim import SGD, Adam, AdamW, lr_scheduler
 
from lib.datasets.data_loader_palm import DataLoader
 

# pklnet
from lib.models.nets.pklnet import  pklnet, SegFocalLoss, EdgeAwareLoss
import lib.models.nets.dsntnn as dsntnn

from lib.utils.lite import *
    

random.seed(1)
torch.manual_seed(1)


MAX_ITER_EPOCH = 2000


batch_size = 8#14#8#12#16#8

# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/Tongji/'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/IITD/'
dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/ALL/'


data_loader = DataLoader(root_dir = dataset_dir, batch_size=batch_size)

train_loader = data_loader.get_trainloader()
# val_loader = data_loader.get_valloader()
# test_loader = data_loader.get_testloader()

NUM_KP = 2+1

net = pklnet(NUM_KP=NUM_KP)
# print(net)
# net.load_state_dict(torch.load('./net_params.pth'))


optimizer = AdamW(group_weight(net), lr=0.0001, betas=[0.9, 0.999], eps=1e-08, weight_decay=0.01)
# optimizer = AdamW(net.parameters(), lr=0.0001, betas=[0.9, 0.999], eps=1e-08, weight_decay=0.01)
 
# scheduler = lr_scheduler.StepLR(optimizer, step_size=500, gamma=0.9) 
scheduler = lr_scheduler.StepLR(optimizer, step_size=200, gamma=0.5) # 0.6


seg_loss = SegFocalLoss(class_num=net.bre_segment.num_classes) # net.num_classes
mse_loss = nn.MSELoss()
edgedis_loss =EdgeAwareLoss(kpNum=41) ######


net.train()


seg_loss.train()
mse_loss.train()
edgedis_loss.train()


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# device = 'cpu'

print(device)

net.to(device)
net.float()


input_keys = ['img']
target_keys = ['labelmap', 'keypoint'] # 'edge'



if not os.path.exists('rst/imgs'):
    os.makedirs('rst/imgs')

if not os.path.exists('rst/checkpoints'):
    os.makedirs('rst/checkpoints')


logfile = open(os.path.join('rst', 'log.txt'), 'w')

loss1 = []
loss2 = []
loss3 = []
loss4 = []
loss5 = []


for epoch in range(MAX_ITER_EPOCH+1):
    for i, data_dict in enumerate(train_loader):
            net.train()


            optimizer.zero_grad()
            # scheduler.step(i)

            itern = i
           

            inputs = [data_dict[k] for k in input_keys]
            batch_size = inputs[0].size(0)
            targets = [data_dict[k] for k in target_keys]

            labelimgs = targets[0]

            # print('......input..............', labelimgs.shape, labelimgs.max(), labelimgs.min())

            imgs = inputs[0].to(device)
            labelimgs = targets[0].to(device)
            keypoints = targets[1].to(device)

            outputs = net(imgs)

            (outkp, aux, out, stnmap, post_feat, heatmaps, weight) = outputs
        
            


            ###------------
            segloss = seg_loss((aux, out), labelimgs)
          
            mse_fv = mse_loss(outkp[:, :4], keypoints[:,:4])
         
            # mse_roi = mse_loss(outkp[:, 4:12], keypoints[:, 4:12]) 
            xs = torch.mean(keypoints[:, 4:12:2], dim=1, keepdim=True)
            # print(a.shape)
            ys = torch.mean(keypoints[:, 5:12:2], dim=1, keepdim=True)
            # print(b.shape)
            cs = torch.cat((xs, ys), dim=1)
            mse_roi = mse_loss(outkp[:, 4:6], cs) 

            disloss, idx1, idx2 = edgedis_loss(outkp, keypoints[:, 12:])           
          
 
            # t = keypoints[:,:2*6]
            # t = (t*2+1)/torch.Tensor([300., 400]).to(device).repeat(batch_size, 6)-1                        
            t = keypoints[:,:2*NUM_KP]
            t = (t*2+1)/torch.Tensor([300., 400]).to(device).repeat(batch_size, NUM_KP)-1                        
            reg_losses, gauss = dsntnn.js_reg_losses(heatmaps, t.reshape(batch_size, NUM_KP, 2), sigma_t=1)#1 #1.5 #5.0 #10.0 #15.0
            loss_heatmap = dsntnn.average_loss(reg_losses)

            # loss = 0*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            # loss = 1*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            # loss = 0.2*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            # loss = 0.5*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            # loss = 0.75*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            # loss = 0.25*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            
            loss = 1*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.1*loss_heatmap/loss_heatmap.item()
            
            ## loss = 1*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 1*loss_heatmap/loss_heatmap.item()
            ## loss = 1*segloss/segloss.item() + 0.5*mse_fv/mse_fv.item() + 0.1*disloss/disloss.item() +  0.1*mse_roi/mse_roi.item()  + 0.5*loss_heatmap/loss_heatmap.item()
            ## loss = 2*segloss/segloss.item() + 1*mse_fv/mse_fv.item() + 0.5*disloss/disloss.item() + 0.5*mse_roi/mse_roi.item() + 1*loss_heatmap/loss_heatmap.item()


            if i==0:                
                a = segloss.item()
                b = mse_fv.item()
                c = disloss.item()
                d = mse_roi.item()
                e = loss_heatmap.item()
            else:
                a += segloss.item()
                b += mse_fv.item()
                c += disloss.item()
                d += mse_roi.item()
                e += loss_heatmap.item()

            if i == len(train_loader) - 1:
                t_num = len(train_loader)
                loss1.append(a/t_num)
                loss2.append(b/t_num)
                loss3.append(c/t_num)
                loss4.append(d/t_num)
                loss5.append(e/t_num)


            
            if i % 20 == 0:
                print('epoch %d, iter %d, lr %f, === segLoss %f, fvKp %f, roiKp %f, edgeDis %f, heatmap %f, ===> LOSS %f w[0] %.3f'%(epoch, i, scheduler.get_last_lr()[0], segloss.item(), mse_fv.item(), mse_roi.item(), disloss.item(), loss_heatmap.item(), loss.item(), weight[0].item()))#weight[0,0].item()))#weight[0,0].item()))#
                logfile.write('epoch %d, iter %d, lr %f, === segLoss %f, fvKp %f, roiKp %f, edgeDis %f, heatmap %f, ===> LOSS %f w[0] %f\n'%(epoch, i, scheduler.get_last_lr()[0], segloss.item(), mse_fv.item(), mse_roi.item(), disloss.item(), loss_heatmap.item(), loss.item(), weight[0].item()))#weight[0,0].item()))#weight[0,0].item()))#
            


            # train_losses.update(display_loss.item(), batch_size)
            # self.loss_time.update(time.time() - loss_start_time)

            # backward_start_time = time.time()

            loss.backward()
            optimizer.step()


            if i % 200 == 0 and epoch > 0:
                print('start to save the .pth ...')
                torch.save(net.state_dict(), 'net_params.pth')
                torch.save(net.state_dict(), './rst/checkpoints/net_params.pth')
                print('saved!')


      
            # if epoch < 3 or epoch % 8 == 0:
            if 1:
                visualization((imgs, labelimgs, keypoints), outputs, (idx1, idx2), epoch, itern) 

    scheduler.step()

    if epoch % 50 == 0:
        torch.save(net.state_dict(), './rst/checkpoints/net_params_%d.pth'%epoch)
        print('saved!')
    

    path_rst = './rst/'
    plt.figure()
    plt.plot(range(1, len(loss1)+1), loss1, 'k', label='Segment loss')
    # plt.yscale('log')
    plt.ylim([0.0001, 0.03])
    plt.legend()
    plt.xlabel('Epoch number')
    plt.ylabel('Loss')
    plt.grid()
    plt.savefig(os.path.join(path_rst, 'loss_seg.png'))
    plt.close()
    
    plt.figure()
    plt.plot(range(1, len(loss2)+1), loss2, 'r', label='Finger valley kp localization loss')
    plt.plot(range(1, len(loss3)+1), loss3, 'b-', label='Edge-min distance loss')
    # plt.yscale('log')
    plt.ylim([0, 100])
    plt.legend()
    plt.xlabel('Epoch number')
    plt.ylabel('Loss')
    plt.grid()
    plt.savefig(os.path.join(path_rst, 'loss_fingerValley.png'))
    plt.close()
    
    plt.figure()
    plt.plot(range(1, len(loss4)+1), loss4, 'r', label='ROI kp loss')
    # plt.yscale('log')
    plt.ylim([0, 200])
    plt.legend()
    plt.xlabel('Epoch number')
    plt.ylabel('Loss')
    plt.grid()
    plt.savefig(os.path.join(path_rst, 'loss_roi.png'))
    plt.close()

    plt.figure()
    plt.plot(range(1, len(loss5)+1), loss5, 'r-', label='Heatmap loss')
    plt.legend()
    plt.xlabel('Epoch number')
    plt.ylabel('Loss')
    plt.grid()
    plt.savefig(os.path.join(path_rst, 'loss_hm.png'))
    plt.close()

    with open(os.path.join(path_rst, 'epoch_losses=seg_fv_dis_roi_hm.txt'), 'w') as fid:
        for k in range(len(loss1)):
            fid.write('%.4f %.4f %.4f %.4f %.4f \n'%(loss1[k], loss2[k], loss3[k], loss4[k], loss5[k]))
    
#---

torch.save(net.state_dict(), './rst/checkpoints/net_params_final.pth')
print('saved!')
logfile.close()
print('done!')
