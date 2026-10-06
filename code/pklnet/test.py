import argparse

import torch
import torch.nn as nn
import torch.nn.functional as F


import random
import numpy as np
import cv2
import os


# from lib.utils.tools.configer import Configer
# from torch.optim import SGD, Adam, AdamW, lr_scheduler
# import lib.models.nets.dsntnn as dsntnn
# from lib.vis.seg_visualizer_palm import SegVisualizer

 
from lib.datasets.data_loader_palm import DataLoader 
from lib.models.nets.pklnet import  pklnet, SegFocalLoss, EdgeAwareLoss
import roiExtractor
    

batch_size = 8#12#8



# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/REST/'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/CASIA-Multi-Spectral-PalmprintV1/images/'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/rpg1k/img/'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/internet/'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/CASIA'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/ALL/test/image/'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/hards'
# dataset_dir = '/media/sunny/CoolFish/exp/dataset/pklnet/free/COEP/'



data_loader = DataLoader(root_dir = dataset_dir, batch_size=batch_size)

# train_loader = data_loader.get_trainloader()
test_loader = data_loader.get_testloader()


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# device = 'cpu'
print(device)


net = pklnet()
# print(net)
net.load_state_dict(torch.load('./net_params_500.pth'))

net.eval()


net.to(device)
net.float()

input_keys = ['img']


if not os.path.exists('./rst_test/imgs'):
    os.makedirs('./rst_test/imgs')

if not os.path.exists('./rst_test/keypoints'):
    os.makedirs('./rst_test/keypoints')

if not os.path.exists('./rst_test/roi'): # from tangent points
    os.makedirs('./rst_test/roi')

# if not os.path.exists('./rst_test/roi_tangent'): # from tangent points
#     os.makedirs('./rst_test/roi_tangent')

# if not os.path.exists('./rst_test/roi_predicted'): # predicted by pklnet
#     os.makedirs('./rst_test/roi_predicted')



for i, data_dict in enumerate(test_loader):
        
        with torch.no_grad():
            
            # inputs = [data_dict[k] for k in input_keys]   
            # inputimgs = inputs[0]     
 
            inputimgs = data_dict['img']   
            # print(inputimgs.shape)   # (8, 3, 400, 300)

            metas = data_dict['meta']
            imgnames = data_dict['name']
            imgpathes = data_dict['imgname']


            outputs = net(inputimgs.to(device))  
  
            (outkp, aux, out, stnmap, post_feat, heatmaps, weight) = outputs    
                
            auximg = aux.detach().cpu().numpy()
            bre = out.detach().cpu().numpy()
            stnmap = stnmap.data.cpu().numpy() 
            outkp = outkp.data.cpu().numpy()

            post_feat = post_feat.detach().cpu().numpy()

            heatmaps = heatmaps.data.cpu().numpy()
            
            batch_size = len(inputimgs)   

                
            
            for k in range(batch_size):
                 
                name = imgnames[k]                
                ori_img_size = metas[k]['ori_img_size']
                img_size = metas[k]['img_size']       

                inputimg = inputimgs[k,:,:,:]
                inputimg = inputimg.permute(1,2,0).numpy()                
                inputimg = ((inputimg-inputimg.min())/(inputimg.max()-inputimg.min()+1e-6)*255).astype(np.uint8)     
                
                outlabel = np.argmax(bre, axis=1)
                outlabel  = outlabel[k,:,:]   
                outlabel = (outlabel-outlabel.min())/(outlabel.max()-outlabel.min()+1e-6)*255
                outlabel = outlabel.astype(np.uint8)

                aux_bg = auximg[k,0,:,:]           
                aux_bg = (aux_bg-aux_bg.min())/(aux_bg.max()-aux_bg.min()+1e-6)*255
                aux_bg = aux_bg.astype(np.uint8)

                aux_fg = auximg[k,1,:,:]           
                aux_fg = (aux_fg-aux_fg.min())/(aux_fg.max()-aux_fg.min()+1e-6)*255
                aux_fg = aux_fg.astype(np.uint8)

                aux_edge = auximg[k,2,:,:]            
                aux_edge = (aux_edge-aux_edge.min())/(aux_edge.max()-aux_edge.min()+1e-6)*255
                aux_edge = aux_edge.astype(np.uint8)            


                bre_bg = bre[k,0,:,:] # 0: background, 1: palm region, 2: palm edge
                bre_bg = (bre_bg-bre_bg.min())/(bre_bg.max()-bre_bg.min()+1e-6)*255
                bre_bg = bre_bg.astype(np.uint8)

                bre_fg = bre[k,1,:,:]
                bre_fg = (bre_fg-bre_fg.min())/(bre_fg.max()-bre_fg.min()+1e-6)*255
                bre_fg = bre_fg.astype(np.uint8)

                bre_edge = bre[k,2,:,:]           
                bre_edge = (bre_edge-bre_edge.min())/(bre_edge.max()-bre_edge.min()+1e-6)*255
                bre_edge = bre_edge.astype(np.uint8)    


                # after stn         
                stnmap_bg = stnmap[k,0,:,:] # 0: background, 1: palm region, 2: palm edge
                stnmap_bg = (stnmap_bg-stnmap_bg.min())/(stnmap_bg.max()-stnmap_bg.min()+1e-6)*255
                stnmap_bg = stnmap_bg.astype(np.uint8)

                stnmap_fg = stnmap[k,1,:,:] # 0: background, 1: palm region, 2: palm edge
                stnmap_fg = (stnmap_fg-stnmap_fg.min())/(stnmap_fg.max()-stnmap_fg.min()+1e-6)*255
                stnmap_fg = stnmap_fg.astype(np.uint8)

                stnmap_edge = stnmap[k,2,:,:] # 0: background, 1: palm region, 2: palm edge
                stnmap_edge = (stnmap_edge-stnmap_edge.min())/(stnmap_edge.max()-stnmap_edge.min()+1e-6)*255
                stnmap_edge = stnmap_edge.astype(np.uint8)    

                stnmap_bg_ = stnmap[k,3,:,:] 
                stnmap_bg_ = (stnmap_bg_-stnmap_bg_.min())/(stnmap_bg_.max()-stnmap_bg_.min()+1e-6)*255
                stnmap_bg_ = stnmap_bg_.astype(np.uint8)

                stnmap_fg_ = stnmap[k,4,:,:] 
                stnmap_fg_ = (stnmap_fg_-stnmap_fg_.min())/(stnmap_fg_.max()-stnmap_fg_.min()+1e-6)*255
                stnmap_fg_ = stnmap_fg_.astype(np.uint8)

                stnmap_edge_ = stnmap[k,5,:,:] 
                stnmap_edge_ = (stnmap_edge_-stnmap_edge_.min())/(stnmap_edge_.max()-stnmap_edge_.min()+1e-6)*255
                stnmap_edge_ = stnmap_edge_.astype(np.uint8)    
        
                ## enlarge the stnmaps
                # stnmap_bg = cv2.resize(stnmap_bg, (300,400))
                # stnmap_fg = cv2.resize(stnmap_fg, (300,400))
                # stnmap_edge = cv2.resize(stnmap_edge, (300,400))
                # stnmap_bg_ = cv2.resize(stnmap_bg_, (300,400))
                # stnmap_fg_ = cv2.resize(stnmap_fg_, (300,400))
                # stnmap_edge_ = cv2.resize(stnmap_edge_, (300,400))               
                

                hms = np.zeros((heatmaps.shape[2], heatmaps.shape[3]))
                for i in range(heatmaps.shape[1]):
                    hm = heatmaps[0, i, :,:]
                    hm = (hm-hm.min())/(hm.max()-hm.min()+1e-6)*255
                    hm = hm.astype(np.uint8)
                    hms += hm                
                hms = (hms-hms.min())/(hms.max()-hms.min()+1e-6)*255
                hms = hms.astype(np.uint8)
                hms = cv2.resize(hms, (300,400))
                              
               
                palmimg = inputimg

                palmimg = cv2.cvtColor(palmimg, cv2.COLOR_BGR2HSV)
                # palmimg[:,:,-1] = (palmimg[:,:,-1]*0.6).astype(np.uint8)
                predictmap = cv2.cvtColor(palmimg, cv2.COLOR_HSV2BGR)


                kp = outkp[k,:].astype(np.int32)

                # roiExtractor.drawROI(predictmap, kp)
                anticlock = roiExtractor.isAntiClock(kp[:6]) # (kp[4:10])
                ps = np.array(roiExtractor.getROIckp(kp[0:2], kp[2:4], anticlock)).astype(np.int32)
                roiExtractor.drawROI(predictmap, [kp[0], kp[1], kp[2], kp[3], ps[0][0], ps[0][1], ps[1][0], ps[1][1], ps[2][0], ps[2][1], ps[3][0], ps[3][1]])
                kp = np.array([kp[0], kp[1], kp[2], kp[3], ps[0][0], ps[0][1], ps[1][0], ps[1][1], ps[2][0], ps[2][1], ps[3][0], ps[3][1]])


                cv2.imshow("aux_bg", aux_bg)
                cv2.imshow("aux_fg", aux_fg)
                cv2.imshow("aux_edge", aux_edge)

                cv2.imshow("bre_bg", bre_bg)  
                cv2.imshow("bre_fg", bre_fg)                      
                cv2.imshow("bre_edge", bre_edge)

                cv2.imshow("stnmap_bg", stnmap_bg)
                cv2.imshow("stnmap_fg", stnmap_fg)
                cv2.imshow("stnmap_edge", stnmap_edge)   
                cv2.imshow("stnmap_bg_", stnmap_bg_)
                cv2.imshow("stnmap_fg_", stnmap_fg_)
                cv2.imshow("stnmap_edge_", stnmap_edge_) 

                cv2.imshow("inputimg", inputimg)  
                cv2.imshow('heatmaps', hms)                
                cv2.imshow("outlabel", outlabel)
                cv2.imshow("predictmap", predictmap)


                # cv2.imwrite('./rst_test/imgs/%s_heatmaps.png'%(name), hms)  
                # cv2.imwrite('./rst_test/imgs/%s_outlabel.png'%(name), outlabel)  
                cv2.imwrite('./rst_test/imgs/%s_predictmap.png'%(name), predictmap) 


                if 0:
                    for i in range(post_feat.shape[1]):            
                        tmpimg = post_feat[0,i,:,:]
                        tmpimg = (tmpimg-tmpimg.min())/(tmpimg.max()-tmpimg.min()+1e-6)*255
                        tmpimg = tmpimg.astype(np.uint8)
                        post_feat[0,i,:,:] = tmpimg
                        # cv2.imshow("post_feat_%d"%(i), tmpimg)
                        cv2.imwrite("./rst_test/imgs/%s_post_feat_%d.png"%(name, i), tmpimg)

                if 0:                  
                    cv2.imwrite('./rst_test/imgs/%s_inputimg.png'%(name), inputimg)     

                    cv2.imwrite('./rst_test/imgs/%s_aux_edge.png'%(name), aux_edge)  
                    cv2.imwrite('./rst_test/imgs/%s_aux_fg.png'%(name), aux_fg)  
                    cv2.imwrite('./rst_test/imgs/%s_aux_bg.png'%(name), aux_bg) 

                    cv2.imwrite('./rst_test/imgs/%s_bre_edge.png'%(name), bre_edge)  
                    cv2.imwrite('./rst_test/imgs/%s_bre_fg.png'%(name), bre_fg)  
                    cv2.imwrite('./rst_test/imgs/%s_bre_bg.png'%(name), bre_bg)

                    cv2.imwrite('./rst_test/imgs/%s_stnmap_edge.png'%(name), stnmap_edge)  
                    cv2.imwrite('./rst_test/imgs/%s_stnmap_fg.png'%(name), stnmap_fg)  
                    cv2.imwrite('./rst_test/imgs/%s_stnmap_bg.png'%(name), stnmap_bg)   

                    cv2.imwrite('./rst_test/imgs/%s_stnmap_edge_.png'%(name), stnmap_edge_) 
                    cv2.imwrite('./rst_test/imgs/%s_stnmap_fg_.png'%(name), stnmap_fg_)  
                    cv2.imwrite('./rst_test/imgs/%s_stnmap_bg_.png'%(name), stnmap_bg_)   


                # ROI extraction -----------------------------
                w, h = ori_img_size
                # print(h,w)

                if h >= w:
                    if float(h/w) > 4/3.:
                        W = int(400.*w/h)
                        H = 400   
                        ratio = float(h)/H 
                    else:
                        W = 300
                        H = int(300.*h/w)
                        ratio = float(w)/W 
                   

                    kp = (kp*ratio).astype(np.int32)

                    # print(kp, ratio)

                    with open('./rst_test/keypoints/%s.txt'%name, 'w') as f:
                        f.write('%d %d %d %d %d %d %d %d %d %d %d %d\n'%tuple(kp))

                    orikp = kp

                else: # rotated
                    h_ = w
                    w_ = h

                    if float(h_/w_) > 4/3.:
                        W = int(400.*w_/h_)
                        H = 400   
                        ratio = float(h_)/H 
                    else:
                        W = 300
                        H = int(300.*h_/w_)
                        ratio = float(w_)/W 

                    kp = (kp*ratio).astype(np.int32)

                    with open('./rst_test/keypoints/%s.txt'%name, 'w') as f:
                        f.write('%d %d %d %d %d %d %d %d %d %d %d %d\n'%(kp[1], w_-kp[0], kp[3], w_-kp[2], kp[5], w_-kp[4], kp[7], w_-kp[6], kp[9], w_-kp[8], kp[11], w_-kp[10]))
                
                    orikp = np.array([kp[1], w_-kp[0], kp[3], w_-kp[2], kp[5], w_-kp[4], kp[7], w_-kp[6], kp[9], w_-kp[8], kp[11], w_-kp[10]])

                kp = orikp
                c1_ = (kp[0], kp[1])
                c2_ = (kp[2], kp[3])
                r1_ = (kp[4], kp[5])
                r2_ = (kp[6], kp[7])
                r3_ = (kp[8], kp[9])
                r4_ = (kp[10], kp[11])


                print(imgpathes[k])

                oriimg = cv2.imread(imgpathes[k], 1)

                # ori = oriimg.copy()
                # roiExtractor.drawROI(ori, kp)
                # cv2.imwrite('./rst_test/imgs/%s_ori.png'%(name), ori) 
                # cv2.imshow('oriimg roi', ori)

                oriimg = cv2.cvtColor(oriimg, cv2.COLOR_BGR2GRAY)
                # cv2.imshow('oriimg', oriimg)

                anticlock = roiExtractor.isAntiClock(kp[:6])
                ps = roiExtractor.getROIckp(np.array(c1_), np.array(c2_), anticlock)  # <=========== ROI parameters: alpha, beta 
                roi = roiExtractor.getROIimg(oriimg, ps, 128, 1.0)  # <=========== ROI size
                # print(ps)         
                # print(roi)

                if roi is not None:
                    cv2.imwrite('./rst_test/roi/%s.bmp'%(name), roi)     
                cv2.imshow('roi', roi)

                # if roi is not None:
                #     cv2.imwrite('./rst_test/roi_tangent/%s.bmp'%(name), roi)     
                # cv2.imshow('roi_tangent', roi)

                # roi = roiExtractor.getROIimg(oriimg, [r1_, r2_, r3_, r4_], 128, 1.0)  
                # if roi is not None:
                #     cv2.imwrite('./rst_test/roi_predicted/%s.bmp'%(name), roi)     
                # cv2.imshow('roi_predicted', roi)

                cv2.waitKey(1) 