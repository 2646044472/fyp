##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Clockwise and Counterclockwise ROI Extraction for PKLNet
## Created by: Xu Liang
## Harbin Institute of Technology, Shenzhen
## xuliangcs@gmail.com
## Copyright (c) 2022
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import numpy as np
import cv2


def isAntiClock(xyxyxy):
    assert len(xyxyxy) == 6
    x1, y1, x2, y2, x3, y3 = xyxyxy
    f = x1*y2+x2*y3+x3*y1-y1*x2-y2*x3-y3*x1 
    if f < 0:
        return True 
    else:
        return False
    


def getROIckp(pt1, pt2, anticlock=True, alpha=0.15, beta=1.2):      
    '''
    for PKLNet
    (pt1, pt2) + anticlock + (alpha, beta) ===> ROI 
    ps: double coordinates
    o----->x
    |y
    '''        
    if pt1 is None or pt2 is None:
        return None               
 
    x1, y1 = pt1
    x2, y2 = pt2

    d = np.sqrt((x1-x2)**2+(y1-y2)**2)
    if d < 1e-5:
        return None
    
    side = d*beta
    hside = side/2.0
    
    mx, my = (x1+x2)/2, (y1+y2)/2
    dy = y2-y1  
    dx = x2-x1   
    if x1 == x2:
        if y1 < y2:
            theta = np.pi/2
        else:
            theta = -np.pi/2
    else:
        theta = np.arctan2(dy, dx)
    # print(theta/np.pi*180)

    if anticlock == True:
        flag = 1
    else:
        flag = -1

    gamma = theta - flag*np.pi/2

    costheta = np.cos(theta)
    sintheta = np.sin(theta)

    cosgamma = np.cos(gamma)
    singamma = np.sin(gamma)

    costheta2 = np.cos(theta-np.pi)
    sintheta2 = np.sin(theta-np.pi)

    l = alpha*d 

    m1x = mx + l*cosgamma
    m1y = my + l*singamma

    m2x = mx + (l+2*hside)*cosgamma
    m2y = my + (l+2*hside)*singamma

    p0 = (m1x + hside*costheta2, m1y + hside*sintheta2) 
    p1 = (m1x + hside*costheta, m1y + hside*sintheta) 
    
    p2 = (m2x + hside*costheta, m2y + hside*sintheta) 
    p3 = (m2x + hside*costheta2, m2y + hside*sintheta2) 
    
    ps = [p0, p1, p2, p3]

    return ps



def getROIimg(image, ps, side=128, ratio=1):  
    '''Extract the ROI image from the given four corner points 
     (perspective transformation, warp perspective) 
    ps: a list of 4 points, [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]    
    side: size of the output ROI image
    ratio: the enlarge ratio of the ps (ps ---> image) 
    '''    
       
    if image is None or ps is None or len(ps)<4 or side <= 0:
        print('getROIimg: input error!')
        return None          

    # roi_corner_points = np.array([ps[:2], ps[2:4], ps[4:6], ps[6:8]])
    roi_corner_points = ps[:4]

    src = np.array(roi_corner_points, dtype="float32")

    src = src*ratio

    # print('ps', ps)

    anticlock = isAntiClock(np.array(ps[:3]).reshape(-1))
    # if anticlock:
    #     dst = np.array([[0, 0], [0, side], [side, side], [side, 0]], dtype='float32')        
    # else:
    #     dst = np.array([[0, side], [0, 0], [side, 0], [side, side]],  dtype='float32') 
    if anticlock:
        dst = np.array([[side, 0], [0, 0], [0, side], [side, side]], dtype='float32')     
    else:
        dst = np.array([[0, 0], [side, 0], [side, side], [0, side]], dtype='float32') 

    # print('ROI corner points: ', src, dst)
    # print('anticlock: ', anticlock)

    try:
        M = cv2.getPerspectiveTransform(src, dst)       
        warped = cv2.warpPerspective(image, M, (side, side)) 
    except:
        print('getROIimg: calculating perspective matrix failed!')
        return None

    if warped.ndim == 3:
        warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)  
    
    return warped


def drawROI(img, kp):
    '''
    draw the ROI kps (t1, t2; r1~r4) on the given image
    '''
    c1_ = (kp[0], kp[1])
    c2_ = (kp[2], kp[3])

    r1_ = (kp[4], kp[5])
    r2_ = (kp[6], kp[7])
    r3_ = (kp[8], kp[9])
    r4_ = (kp[10], kp[11])

    cv2.line(img, r1_, r2_, thickness=3, color=(255,210,50))
    cv2.line(img, r2_, r3_, thickness=3, color=(255,210,50))
    cv2.line(img, r3_, r4_, thickness=3, color=(255,210,50))
    cv2.line(img, r4_, r1_, thickness=3, color=(255,210,50))

    cv2.circle(img, r1_, radius=5, thickness=-1, color=(255,0,0))
    cv2.circle(img, r2_, radius=5, thickness=-1, color=(0,0,0))
    cv2.circle(img, r3_, radius=5, thickness=-1, color=(0,255, 255))
    cv2.circle(img, r4_, radius=5, thickness=-1, color=(255,0,255))

    # # finger valley edges
    # for k in range(len(x1)):
    #     cv2.circle(img, (int(x1[k]), int(y1[k])), radius=1, thickness=2, color=(100, 100, 255))
    #     cv2.circle(img, (int(x2[k]), int(y2[k])), radius=1, thickness=2, color=(255, 100, 100)) 
    # cv2.circle(img, cen1, radius=4, thickness=2, color=(0,0,0))
    # cv2.circle(img, cen2, radius=4, thickness=2, color=(0, 255,255))            

    cv2.line(img, c1_, c2_, thickness=2, color=(255,210,50))

    cv2.circle(img, c1_, radius=5, thickness=-1, color=(0,0,255))
    cv2.circle(img, c2_, radius=5, thickness=-1, color=(0,255,0))