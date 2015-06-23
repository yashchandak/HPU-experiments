# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:34:29 2015

@author: student


===== INstructions =========

Esc : to exit program
p   : pause program timer
Enter: next image

Left MButton down : mark top left corner of bbox
left Mbutton up   : mark bottom right corner of bbox
right MButton down: cancel drawn bbox
"""



#!/usr/bin/env python3
import cv2, time, os
import numpy as np
"""=================================== Evaluator ================================"""
def ratio(a,b):
    XA1,YA1,wa,ha=a
    XB1,YB1,wb,hb=b
    XA2=XA1+wa
    YA2=YA1+ha
    XB2=XB1+wb
    YB2=YB1+hb
    #intersection = max(0, min(x1, x2))
    I = max(0, min(XA2, XB2) - max(XA1, XB1)) * max(0, min(YA2, YB2) - max(YA1, YB1))
    U = wa*ha + wb*hb - I
    return I*1.0/U
    

def get_accuracy(HPUflag, resultfile):
    #key=0
    #cpu=0
    totalCPU=0
    totalGround=220
    timetaken=0
    res=[]
    if HPUflag:
        key=open('overlapKeyHPU.txt', 'w')
        cpu=open(resultfile, 'r')
    else:
        key=open('overlapKeyCPU.txt', 'w')
        cpu=open(resultfile, 'r')
    
    ground=open('ground.txt', 'r')
    gTruth = ground.read().split()
    gTruth = [int(item) for item in gTruth]
    #print gTruth
    
    ptr=0
    truthBbox=[]
    for i in xrange(1,101):
        rects=[]
        imgNo = gTruth[ptr]
        bboxNum = gTruth[ptr+1]
        ptr=ptr+2
        for j in xrange(bboxNum):
            rects.append( (gTruth[ptr], gTruth[ptr+1], gTruth[ptr+2], gTruth[ptr+3]) )
            ptr=ptr+4
        
        truthBbox.append(rects)
    
    cpuRes = cpu.read().split()
    
    ptr=0
    cpuBbox=[]
    for i in xrange(1,101):
        rects=[]
        imgNo = int(cpuRes[ptr])
        bboxNum = int(cpuRes[ptr+1])
        totalCPU = totalCPU + bboxNum
        ptr=ptr+2
        if HPUflag:
            timetaken=timetaken+float(cpuRes[ptr])
            ptr=ptr+1
        for j in xrange(bboxNum):
            rects.append( (int(cpuRes[ptr]), int(cpuRes[ptr+1]), int(cpuRes[ptr+2]), int(cpuRes[ptr+3])) )
            #print (gTruth[ptr], gTruth[ptr+1], gTruth[ptr+2], gTruth[ptr+3])
            ptr=ptr+4
            
        
        cpuBbox.append(rects)
        #ptr=ptr+1
    #print cpuBbox
    temp=0
    for i in xrange(1, 101):
        for gbox in truthBbox[i-1]:
            x=(gbox[0], gbox[1], gbox[2], gbox[3])
            maxi=0
            for cbox in cpuBbox[i-1]:
                y=(cbox[0], cbox[1], cbox[2], cbox[3])
                if maxi < ratio(x,y):
                    maxi=ratio(x,y)
            key.write(str(round(maxi,6))+'\n')
            if maxi >= 0.5:
                temp=temp+1
            res.append(round(maxi,6))
    
    print temp
    precision=sum([1 for iou in res if iou>=0.5])*1.0/totalGround
    recall=sum([1 for iou in res if iou>=0.5])*1.0/totalCPU
    fscore=precision*recall*2.0/(precision+recall)
    print 'correct:',sum([1 for iou in res if iou>=0.5])
    print 'detected:',totalCPU
    print 'precision:',precision
    print 'recall:',recall
    print 'fscore:',fscore    
    if HPUflag:
        print 'time taken:',timetaken
    key.close()
    ground.close()
    cpu.close()
    return (precision, recall, fscore)
    
#get_accuracy(False,'CPU.txt' )
"""============================ end of evaluator ===================================="""






count=0
lst = []
def on_event(event,x,y,flags,param):
    global count
    global lst
    global draw_image
    global startpointx,startpointy,rectangle
    
    if event == cv2.EVENT_LBUTTONDOWN:
        rectangle = True
        startpointx = x
        startpointy = y
        draw_image = resized.copy()
        cv2.rectangle(draw_image,(x,y),(x,y),(0,255,0))
        
    elif event == cv2.EVENT_RBUTTONDOWN:
        #cancel the drawn rectangle
        rectangle = False
        draw_image = resized.copy()

    elif event == cv2.EVENT_LBUTTONUP:
        if rectangle:
            rectangle = False
            cv2.rectangle(draw_image,(startpointx,startpointy),(x,y),(0,255,0))
            count=count+1
            #print int(startpointx/ration),int(startpointy/ration),int(x/ration)-int(startpointx/ration),int(y/ration)-int(startpointy/ration)
            #print count
            lst.append((int(startpointx/ration),int(startpointy/ration),int(x/ration)-int(startpointx/ration),int(y/ration)-int(startpointy/ration)))
   
    elif event == cv2.EVENT_MOUSEMOVE:
        if rectangle:
            #print('Move',startpointx,startpointy,x,y)#debugging
            draw_image = resized.copy()
            cv2.rectangle(draw_image,(startpointx,startpointy),(x,y),(0,255,0),3    )
            
            #highlighting the marked region
            
#            for i in range(startpointx, x):
#                for j in range(startpointy, y):
#                    draw_image[j][i] = min(255, draw_image[j][i]+50)



CPU=open('fp_removed.txt', 'r')
data=CPU.read().split()
CPU.close()

data=[int(item) for item in data]
CPUbox=[[0]]
ptr = 0

while ptr<len(data):
    rects=[]
    ptr=ptr+1
    bboxNum=data[ptr]
    for j in xrange(bboxNum):
        rects.append([data[ptr+1],data[ptr+2],data[ptr+3],data[ptr+4], data[ptr+5]])
        ptr=ptr+5
    CPUbox.append(rects)
    ptr=ptr+1
    
totaltime = 0
out = open('fp_removed.txt','w')    
temp = open('foundLocations_HPU.txt', 'w')
for i in range(1,101):
    print 'image no: ', i    
    
    Path = 'D:/ToDo/research_santa_cruz/train/'+str(i)+'.png'
    image_float_size = 600.0
    image_int_size = int(image_float_size)
    color = [0,255,0]
    rectangle = False
    # Read the image and convert it into gray
    image = cv2.imread(Path)
    gray_image = image
    #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #print gray_image.shape
    for x,y,w,h,conf in CPUbox[i]:
        #print x,y,w,h
        cv2.rectangle(gray_image,(x,y),(x+w,y+h),(0,255,0)) 
    
    # resize the image
    ration = image_float_size / gray_image.shape[1]
    dim = (image_int_size,int(gray_image.shape[0]*ration))
    resized = cv2.resize(gray_image, dim, interpolation = cv2.INTER_AREA)
    draw_image = resized.copy()
    #print ration
    # set window for the image
    cv2.namedWindow('window - enter for next image, Esc to exit, p to pause')
    
    # mouse callback
    cv2.setMouseCallback('window - enter for next image, Esc to exit, p to pause',on_event)
    flag=0
    
    start = time.time()
    lst=[]
    count=len(CPUbox[i])
    paused = 0
    while True:
        cv2.imshow('window - enter for next image, Esc to exit, p to pause', draw_image)
        ch = 0xFF & cv2.waitKey(1)
        if ch == 27 or ch ==13:
            elapsed = time.time()-start-paused  
            totaltime = totaltime + elapsed
            out.write(str(i)+' '+str(count))
            temp.write(str(i)+' '+str(count))
            for x,y,w,h,conf in CPUbox[i]:
                out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h)+' '+str(conf))
                temp.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            for x,y,w,h in lst:
                out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h)+' 99999')
                temp.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            out.write('\n')
            temp.write('\n')
            if ch == 27:
                flag=1
            break
        
        #when 'p' is pressed
        elif ch==112:
            print 'paused..',
            
            paused = time.time()
            
            while True:
                ch = cv2.waitKey(1)
                if ch ==112:    
                    paused = time.time() - paused
                    break
                
            print 'for', paused        
    
    if flag==1:
        break
    
out.close()
temp.close()

results = get_accuracy(False,'foundLocations_HPU.txt')

#cache the results
out=open('HpuResults.txt', 'a')
out.write(str(results[0])+ ' '+ str(results[1])+' '+ str(results[2]) +' '+ str(totaltime) + '\n\n')
out.close()
    
cv2.destroyAllWindows()
