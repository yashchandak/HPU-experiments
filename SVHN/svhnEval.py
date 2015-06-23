# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 11:01:16 2015

@author: student
"""
import cv2, time
import numpy as np

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
    
"""a=(1,2,3,4)
b=(1,1,3,4)
ratio(a,b)"""

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
            #print (gTruth[ptr], gTruth[ptr+1], gTruth[ptr+2], gTruth[ptr+3])
            ptr=ptr+4
            #if HPUflag:
            #    ptr=ptr+1
        
        truthBbox.append(rects)
        #ptr=ptr+1
        
    
    cpuRes = cpu.read().split()
    #cpuRes = [int(item) for item in cpuRes]
    #print gTruth
    
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
    
get_accuracy(False,'CPU.txt' )
