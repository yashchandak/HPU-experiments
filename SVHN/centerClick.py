# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 13:25:44 2015

@author: student
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:34:29 2015
@author: student
"""

#!/usr/bin/env python3
import cv2, time
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



"""
Returns closest bounding box to (px,py) in the scaled image
"""
def closest(px,py):
    mini=9999999
    for x,y,w,h,c,votes in centerOfMass:
        if (int(c[0]*ration)-px)**2+(int(ration*c[1])-py)**2 < mini:
            mini=(int(c[0]*ration)-px)**2+(int(ration*c[1])-py)**2
            #retval=(x,y,w,h)
            retval = ((int(x*ration),int(ration*y),int(ration*w),int(ration*h)),centerOfMass.index((x,y,w,h,c,votes)), votes)
            
    return retval


"""
For event handling on click and mouse over
(Made some changes here)
"""
def on_event(event,x,y,flags,param):
    global count
    global centerOfMass
    global draw_image
    global startpointx,startpointy,rectangle
    
    if event == cv2.EVENT_LBUTTONDOWN:
        rectangle = True
        startpointx = x
        startpointy = y
        #print('Down',x,y) #debugging
        draw_image = resized.copy()
        #cv2.circle(draw_image, (startpointx, startpointy), 2, (0,255,0))

    elif event == cv2.EVENT_LBUTTONUP:
        rectangle = False
        #print('Up',x,y)
        draw_image = resized.copy()
        rectSelected,pos,votes=closest(x, y)
        cv2.rectangle(draw_image,(rectSelected[0],rectSelected[1]),(rectSelected[0]+rectSelected[2],rectSelected[1]+rectSelected[3]),(0,255,0))
        rectIndex.append(pos)
        #print pos
        count=count+1
        boxList.append( (int(rectSelected[0]/ration), int(rectSelected[1]/ration), int(rectSelected[2]/ration), int(rectSelected[3]/ration), votes) )

    elif event == cv2.EVENT_MOUSEMOVE:
        if True:#rectangle:
            #print('Move',startpointx,startpointy,x,y)#debugging
            draw_image = resized.copy()
            rectSelected,pos,votes=closest(x, y)
            cv2.rectangle(draw_image,(rectSelected[0],rectSelected[1]),(rectSelected[0]+rectSelected[2],rectSelected[1]+rectSelected[3]),(0,255,0))


"""
reads cpu boxes and returns them
"""
def readCPU():
    CPU=open('CPUboxes.txt', 'r')
    data=CPU.read().split()
    data=[int(item) for item in data]
    retval=[]
    retval.append([-1])
    ptr=0
    for i in xrange(1,101):
        rects=[]
        ptr=ptr+1
        bboxNum=data[ptr]
        for j in xrange(bboxNum):
            rects.append( (data[ptr+1],data[ptr+2],data[ptr+3],data[ptr+4]) )
            ptr=ptr+4
        retval.append(rects)
        ptr=ptr+1
        #print i,rects
    CPU.close()
    return retval
"""
reads confidence values and returns them
to make file initially run confWriter.py
"""
def readConf():
    retval=[]
    readIn = open('conf.txt', 'r')
    data=readIn.read().split()
    data=[int(item) for item in data]
    retval.append([-1])
    for i in data:
        retval.append(i)
    readIn.close()
    return retval
"""
Updates confidence values
"""
def writeConf(newConf):
    writeOut = open('conf.txt', 'w')
    ptr=1
    for i in newConf:
        writeOut.write(str(currConf[ptr]+i)+'\n')
        ptr=ptr+1
    writeOut.close()




count=0
centerOfMass=[]
ration=0
boxList=[]
CPUbox=[]
currConf=[]
newConf=[]
rectIndex=[]


CPUbox=readCPU()
currConf=readConf()

out=open('fp_removed.txt', 'w')
res = open('foundLocations_HPU.txt', 'w')
timeout=open('time.txt', 'a')
totaltime=0
##Loop this for 1,2,3,4,...,100.png
confPtr=1
for i in xrange(1,101):
    #reset variables for each image
    count=0
    boxList=[]
    centerOfMass=[]
    rectIndex=[]
    imageConf=[]
    
    #read file
    Path = 'D:/ToDo/research_santa_cruz/train/'+str(i)+'.png'
    
    #change scale of image for proper viewing
    image_float_size = 1000.0
    image_int_size = int(image_float_size)
    

    image = cv2.imread(Path)
    gray_image = image
    for j in xrange(0,len(CPUbox[i])):
        imageConf.append(currConf[confPtr])
        confPtr=confPtr+1
    
    #print imageConf
    #push all bboxes with center of mass
    index=0
    den = 1
    if max(imageConf) != 0:
        den = max(imageConf)
    for x,y,w,h in CPUbox[i]:
        cv2.rectangle(gray_image, (x,y), (x+w,y+h), (0,0,int(255*imageConf[index]/den)), 1)
        centerOfMass.append( (x,y,w,h,(int(x+w/2), int(y+h/2)), imageConf[index]) )
        index=index+1
    
    
    # resize the image
    ration = image_float_size / gray_image.shape[1]
    dim = (image_int_size,int(gray_image.shape[0]*ration))
    global resized
    resized = cv2.resize(gray_image, dim, interpolation = cv2.INTER_AREA)
    draw_image = resized.copy()

    #print ration
    #set window for the image
    cv2.namedWindow('window')
    
    # mouse callback
    cv2.setMouseCallback('window',on_event)
    flag=0
    
    start = time.time()
    temp=0
    while True:
        cv2.imshow('window', draw_image)
        ch = 0xFF & cv2.waitKey(1)
        
        #read spacebar
        if ch == 32:
            print 'pause'
            temp=time.time()
            while True:
                ch2 = 0xFF & cv2.waitKey(1)
                #spacebar to unpause
                if ch2 == 32:
                    print 'unpause'
                    break
            start = start + time.time() - temp
            continue
        
        #escape key to exit
        if ch == 27:
            elapsed = time.time()-start  
            totaltime = totaltime + elapsed
            out.write(str(i)+' '+str(count))
            res.write(str(i)+' '+str(count))
            timeout.write(str(round(elapsed,3))+'\n')
            for x,y,w,h,votes in boxList:
                out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h)+' '+str(votes+1))
                res.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            out.write('\n')
            res.write('\n')
            flag=1
            break
        
        #enter key for next image
        if ch == 13:
            elapsed = time.time()-start
            totaltime = totaltime + elapsed
            out.write(str(i)+' '+str(count))
            res.write(str(i)+' '+str(count))
            timeout.write(str(round(elapsed,3))+'\n')
            for x,y,w,h,votes in boxList:
                out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h)+' '+str(votes+1))
                res.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            out.write('\n')
            res.write('\n')
            break
    #make note of change in confidence for later updation
    for i in xrange(0,len(centerOfMass)):
        if i in rectIndex:
            newConf.append(1)
        else:
            newConf.append(0)
    #print newConf
    if flag==1:
        break
    
cv2.destroyAllWindows()
#update confidence
timeout.write('\n\n')
timeout.close()
writeConf(newConf)
out.close()
res.close()



results = get_accuracy(False,'foundLocations_HPU.txt')

#cache the results
out=open('HpuResults.txt', 'a')
out.write(str(results[0])+ ' '+ str(results[1])+' '+ str(results[2]) +' '+ str(totaltime) + '\n\n')
out.close()
