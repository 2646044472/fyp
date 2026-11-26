"""Project residual encoder as used in the matched 100-person MPD runs."""
import torch.nn as nn

class Block(nn.Module):
 def __init__(self,a,b,s):
  super().__init__();self.main=nn.Sequential(nn.BatchNorm2d(a),nn.Conv2d(a,b,3,1,1,bias=False),nn.BatchNorm2d(b),nn.PReLU(b),nn.Conv2d(b,b,3,s,1,bias=False),nn.BatchNorm2d(b));self.short=nn.Sequential(nn.Conv2d(a,b,1,s,bias=False),nn.BatchNorm2d(b)) if a!=b or s!=1 else nn.Identity()
 def forward(self,x):return self.main(x)+self.short(x)

class Net(nn.Sequential):
 def __init__(self):
  l=[nn.Conv2d(3,64,3,1,1,bias=False),nn.BatchNorm2d(64),nn.PReLU(64)];a=64
  for b in (64,128,256,512):l.extend([Block(a,b,2),Block(b,b,1)]);a=b
  l.extend([nn.BatchNorm2d(512),nn.Flatten(),nn.Linear(512*7*7,512),nn.BatchNorm1d(512)]);super().__init__(*l)
