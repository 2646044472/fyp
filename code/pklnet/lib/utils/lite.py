import torch.nn as nn
import numpy as np
import cv2

# @staticmethod
def group_weight(module):
    group_decay = []
    group_no_decay = []
    # group_stn = []

    for m in module.modules():
        if isinstance(m, nn.Linear):
            group_decay.append(m.weight)
            if m.bias is not None:
                group_no_decay.append(m.bias)
        elif isinstance(m, nn.modules.conv._ConvNd):
            group_decay.append(m.weight)
            if m.bias is not None:
                group_no_decay.append(m.bias)
        else:
            if hasattr(m, "weight"):
                group_no_decay.append(m.weight)
            if hasattr(m, "bias"):
                group_no_decay.append(m.bias)
            if hasattr(m, "absolute_pos_embed"):
                group_no_decay.append(m.absolute_pos_embed)
            if hasattr(m, "relative_position_bias_table"):
                group_no_decay.append(m.relative_position_bias_table)
            if hasattr(m, 's'): ##################### for pklnet only <------
                # print(m)
                group_no_decay.append(m.s)
    
    assert len(list(module.parameters())) == len(group_decay) + len(group_no_decay)

    groups = [
        dict(params=group_decay),
        dict(params=group_no_decay, weight_decay=0.0),
    ]
    return groups

# def _get_parameters(net):
#     bb_lr = []
#     nbb_lr = []
#     params_dict = dict(net.named_parameters())

#     for key, value in params_dict.items():
#         if "backbone" not in key:
#             nbb_lr.append(value)
#         else:
#             bb_lr.append(value)

#     params = [
#         {"params": bb_lr,   "lr": 0.0001},
#         {"params": nbb_lr,  "lr": 0.01}
#     ]
#     return params



def visualization(inputs, outputs, kpidx, epoch, itern):
    (imgs, labelimgs, keypoints) = inputs
    (outkp, aux, out, stnmap, post_feat, heatmaps, weight) = outputs
    (idx1, idx2) = kpidx

    hm_list = []
    for i in range(heatmaps.size(1)):
        hm = heatmaps[0, i, :,:].detach().cpu().numpy()
        hm = (hm-hm.min())/(hm.max()-hm.min()+1e-6)*255
        hm = hm.astype(np.uint8)
        hm = cv2.resize(hm, (300//2,400//2))
        # cv2.imshow('heatmap_%d'%i, hm)
        hm_list.append(hm)

    hms = heatmaps[0,:,:,:].sum(dim=0).squeeze(dim=0).data.cpu().numpy()
    hms = (hms-hms.min())/(hms.max()-hms.min()+1e-6)*255
    hms = hms.astype(np.uint8)
    hms = cv2.resize(hms, (300,400))
    cv2.imshow('heatmaps', hms)
    
    # gs = gauss[0,:,:,:].sum(dim=0).squeeze(dim=0).detach().cpu().numpy()
    # # print(gs.shape)
    # gs = (gs-gs.min())/(gs.max()-gs.min()+1e-6)*255
    # gs = gs.astype(np.uint8)
    # gs = cv2.resize(gs, (300, 400))
    # cv2.imshow('gauss', gs)


    outimg = out.detach().cpu().numpy()
    auximg = aux.detach().cpu().numpy()   

    outlabel = np.argmax(outimg, axis=1)
    outlabel  = outlabel[0,:,:]   
    outlabel = (outlabel-outlabel.min())/(outlabel.max()-outlabel.min()+1e-6)*255
    outlabel = outlabel.astype(np.uint8)  


    aux_bg = auximg[0,0,:,:]           
    aux_bg = (aux_bg-aux_bg.min())/(aux_bg.max()-aux_bg.min()+1e-6)*255
    aux_bg = aux_bg.astype(np.uint8)
    aux_bg = cv2.resize(aux_bg, stnmap.shape[3:1:-1])

    aux_fg = auximg[0,1,:,:]           
    aux_fg = (aux_fg-aux_fg.min())/(aux_fg.max()-aux_fg.min()+1e-6)*255
    aux_fg = aux_fg.astype(np.uint8)
    aux_fg = cv2.resize(aux_fg, stnmap.shape[3:1:-1])

    aux_edge = auximg[0,2,:,:]            
    aux_edge = (aux_edge-aux_edge.min())/(aux_edge.max()-aux_edge.min()+1e-6)*255
    aux_edge = aux_edge.astype(np.uint8)            
    aux_edge = cv2.resize(aux_edge, stnmap.shape[3:1:-1])


    bre_bg = outimg[0,0,:,:]# 0: background, 1: palm region, 2: palm edge
    bre_bg = (bre_bg-bre_bg.min())/(bre_bg.max()-bre_bg.min()+1e-6)*255
    bre_bg = bre_bg.astype(np.uint8)
    bre_bg = cv2.resize(bre_bg, stnmap.shape[3:1:-1])

    bre_fg = outimg[0,1,:,:]#+outimg[0,2,:,:]
    bre_fg = (bre_fg-bre_fg.min())/(bre_fg.max()-bre_fg.min()+1e-6)*255
    bre_fg = bre_fg.astype(np.uint8)
    bre_fg = cv2.resize(bre_fg, stnmap.shape[3:1:-1])

    bre_edge = outimg[0,2,:,:]           
    bre_edge = (bre_edge-bre_edge.min())/(bre_edge.max()-bre_edge.min()+1e-6)*255
    bre_edge = bre_edge.astype(np.uint8)    
    bre_edge = cv2.resize(bre_edge, stnmap.shape[3:1:-1])


     
    


    inputimg = imgs[0,:,:,:].data.cpu() 
    inputimg = inputimg.permute(1,2,0).numpy()                 
    inputimg = ((inputimg-inputimg.min())/(inputimg.max()-inputimg.min()+1e-6)*255).astype(np.uint8)
    # print(inputimg)

    inputlabel = labelimgs[0,:,:].data.cpu().numpy()
    inputlabel[inputlabel==-1] = 0
    inputlabel = ((inputlabel-inputlabel.min())/(inputlabel.max()-inputlabel.min()+1e-6)*255).astype(np.uint8)

    # print(inputimg.min(), inputimg.max(), inputlabel.min(), inputlabel.max())
    
    # print(keypoints.shape)
    kp = keypoints[0].data.cpu().numpy().astype(np.int32) # not uint8 !!!
    c1 = (kp[0], kp[1])
    c2 = (kp[2], kp[3])
    r1 = (kp[4], kp[5])
    r2 = (kp[6], kp[7])
    r3 = (kp[8], kp[9])
    r4 = (kp[10], kp[11])

    inputlabel = cv2.cvtColor(inputlabel, cv2.COLOR_GRAY2BGR)

    cv2.circle(inputlabel, c1, radius=5, thickness=3, color=(0,0,255))
    cv2.circle(inputlabel, c2, radius=5, thickness=3, color=(0,255,0))

    cv2.circle(inputlabel, r1, radius=7, thickness=-1, color=(255,0,0))
    cv2.circle(inputlabel, r2, radius=7, thickness=-1, color=(128,128,255))
    cv2.circle(inputlabel, r3, radius=7, thickness=-1, color=(0,255,255))
    cv2.circle(inputlabel, r4, radius=7, thickness=-1, color=(255,0,255))



    # print(outkp.shape)
    kp = outkp[0,:].data.cpu().numpy().astype(np.int32)
    c1_ = (kp[0], kp[1])
    c2_ = (kp[2], kp[3])
    r1_ = (kp[4], kp[5])
    # r2_ = (kp[6], kp[7])
    # r3_ = (kp[8], kp[9])
    # r4_ = (kp[10], kp[11])

    es = keypoints[0,12:]
    e1 = es[:41*2]
    e2 = es[41*2:] 
    # e1 = es[:101*2]
    # e2 = es[101*2:] 

    x1 = e1[:-1:2]
    y1 = e1[1::2]

    x2 = e2[:-1:2]
    y2 = e2[1::2]

    # print(x1, y1, x2,y2)

    cen1 = (int(e1[idx1[0]*2+0]), int(e1[idx1[0]*2+1]))
    cen2 = (int(e2[idx2[0]*2+0]), int(e2[idx2[0]*2+1]))

    # predictmap = cv2.cvtColor(bre_edge, cv2.COLOR_GRAY2BGR)
    # predictmap = cv2.resize(predictmap, (300, 400))
    predictmap = cv2.cvtColor(inputimg, cv2.COLOR_BGR2GRAY)
    predictmap = cv2.cvtColor(predictmap, cv2.COLOR_GRAY2BGR)


    cv2.circle(predictmap, r1_, radius=15, thickness=2, color=(255,0,0))
    # cv2.circle(predictmap, r1_, radius=7, thickness=-1, color=(255,0,0))
    # cv2.circle(predictmap, r2_, radius=7, thickness=-1, color=(128,128,255))
    # cv2.circle(predictmap, r3_, radius=7, thickness=-1, color=(0,255,255))
    # cv2.circle(predictmap, r4_, radius=7, thickness=-1, color=(255,0,255))

    # edge
    for k in range(len(x1)):
        cv2.circle(predictmap, (int(x1[k]), int(y1[k])), radius=1, thickness=2, color=(100, 100, 255))
        cv2.circle(predictmap, (int(x2[k]), int(y2[k])), radius=1, thickness=2, color=(255, 100, 100))
    

        cv2.circle(predictmap, cen1, radius=4, thickness=2, color=(0,0,0))
    cv2.circle(predictmap, cen2, radius=4, thickness=2, color=(0, 255,255))            

    cv2.circle(predictmap, c1_, radius=5, thickness=3, color=(0,0,255))
    cv2.circle(predictmap, c2_, radius=5, thickness=3, color=(0,255,0))

    cv2.line(predictmap, c1_, cen1, thickness=2, color=(100, 100,255))
    cv2.line(predictmap, c2_, cen2, thickness=2, color=(255, 100,100))


    cv2.imshow("inputimg", inputimg)                        
    cv2.imshow("inputlabel", inputlabel)                    
                            
    cv2.imshow("aux_bg", aux_bg)
    cv2.imshow("aux_fg", aux_fg)
    cv2.imshow("aux_edge", aux_edge)

    cv2.imshow("bre_bg", bre_bg)  
    cv2.imshow("bre_fg", bre_fg)                      
    cv2.imshow("bre_edge", bre_edge)
    cv2.imshow("outlabel", outlabel)
    cv2.imshow("predictmap", predictmap)
    

    stnmap = stnmap.data.cpu().numpy() # 0: background, 1: palm region, 2: palm edge   
    for i in range(stnmap.shape[1]):            
        tmpimg = stnmap[0,i,:,:]
        tmpimg = (tmpimg-tmpimg.min())/(tmpimg.max()-tmpimg.min()+1e-6)*255
        tmpimg = tmpimg.astype(np.uint8)
        stnmap[0,i,:,:] = tmpimg

        cv2.imshow("stnmap_%d"%i, tmpimg)
    
    post_feat = post_feat.data.cpu().numpy() # 0: background, 1: palm region, 2: palm edge   
    for i in range(post_feat.shape[1]):            
        tmpimg = post_feat[0,i,:,:]
        tmpimg = (tmpimg-tmpimg.min())/(tmpimg.max()-tmpimg.min()+1e-6)*255
        tmpimg = tmpimg.astype(np.uint8)
        post_feat[0,i,:,:] = tmpimg

        cv2.imshow("post_feat_%d"%i, tmpimg)


    # if (epoch == 0 and itern % 4 == 0 and itern < 1000) or (epoch % 2 == 0 and itern % 2 == 0 and itern < 200):
    if (epoch < 7 and epoch%2==0 and itern % 10 == 0 and itern <= 200) or (epoch % 50 == 0 and itern % 10 == 0 and itern < 200):
        cv2.imwrite('./rst/imgs/00_inputimg_%04d_%04d.png'%(epoch, itern), inputimg)    
        cv2.imwrite('./rst/imgs/01_inputlabel_%04d_%04d.png'%(epoch, itern), inputlabel) 
        cv2.imwrite('./rst/imgs/02_aux_bg_%04d_%04d.png'%(epoch, itern), aux_bg)    
        cv2.imwrite('./rst/imgs/03_aux_fg_%04d_%04d.png'%(epoch, itern), aux_fg)    
        cv2.imwrite('./rst/imgs/04_aux_edge_%04d_%04d.png'%(epoch, itern), aux_edge)    
        cv2.imwrite('./rst/imgs/05_bre_bg_%04d_%04d.png'%(epoch, itern), bre_bg)    
        cv2.imwrite('./rst/imgs/06_bre_fg_%04d_%04d.png'%(epoch, itern), bre_fg)    
        cv2.imwrite('./rst/imgs/07_bre_edge_%04d_%04d.png'%(epoch, itern), bre_edge)    
        
        for k in range(stnmap.shape[1]):
            cv2.imwrite('./rst/imgs/%02d_stnmap_%04d_%04d_%d.png'%(8+k, epoch, itern, k), stnmap[0, k, :,:])    

        shift = 8+stnmap.shape[1]
        for k in range(post_feat.shape[1]):
            cv2.imwrite('./rst/imgs/%02d_post_feat_%04d_%04d_%d.png'%(shift+k, epoch, itern, k), post_feat[0, k, :,:])   

        shift += post_feat.shape[1]
        for k in range(len(hm_list)):
            cv2.imwrite('./rst/imgs/%02d_heatmaps_%04d_%04d_%d.png'%(shift+k, epoch, itern, k), hm_list[k]) 

        shift += len(hm_list)
        cv2.imwrite('./rst/imgs/%02d_heatmaps_%04d_%04d.png'%(shift, epoch, itern), hms) 

        
        cv2.imwrite('./rst/imgs/%02d_outlabel_%04d_%04d.png'%(shift+1, epoch, itern), outlabel) 
        cv2.imwrite('./rst/imgs/%02d_predictmap_%04d_%04d.png'%(shift+2, epoch, itern), predictmap)              
      
    cv2.waitKey(1)          
    
