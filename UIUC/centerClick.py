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
count=0
centerOfMass=[]
ration=0
def closest(px,py):
    mini=9999999
    for x,y,w,h,c in centerOfMass:
        if (int(c[0]*ration)-px)**2+(int(ration*c[1])-py)**2 < mini:
            mini=(int(c[0]*ration)-px)**2+(int(ration*c[1])-py)**2
            #retval=(x,y,w,h)
            retval = (int(x*ration),int(ration*y),int(ration*w),int(ration*h))
    
    return retval

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
        cv2.circle(draw_image, (startpointx, startpointy), 2, (0,255,0))
        #cv2.rectangle(draw_image,(x,y),(x,y),(0,255,0))

    elif event == cv2.EVENT_LBUTTONUP:
        rectangle = False
        #print('Up',x,y)
        draw_image = resized.copy()
        rectSelected=closest(x, y)
        cv2.rectangle(draw_image,(rectSelected[0],rectSelected[1]),(rectSelected[0]+rectSelected[2],rectSelected[1]+rectSelected[3]),(0,255,0))
        count=count+1
        lst.append( (int(rectSelected[0]/ration), int(rectSelected[1]/ration), int(rectSelected[2]/ration), int(rectSelected[3]/ration)))
        #lst.append((int(startpointx/ration),int(startpointy/ration),int(x/ration)-int(startpointx/ration),int(y/ration)-int(startpointy/ration)))
   
    elif event == cv2.EVENT_MOUSEMOVE:
        if rectangle:
            #print('Move',startpointx,startpointy,x,y)#debugging
            draw_image = resized.copy()
            rectSelected=closest(x, y)
            cv2.rectangle(draw_image,(rectSelected[0],rectSelected[1]),(rectSelected[0]+rectSelected[2],rectSelected[1]+rectSelected[3]),(0,255,0))
            #cv2.rectangle(draw_image,(startpointx,startpointy),(x,y),(0,255,0))


out=open('outputHPU.txt', 'w')
CPU=open('CPUboxes.txt', 'r')
data=CPU.read().split()
data=[int(item) for item in data]
CPUbox=[]
CPUbox.append([0])
ptr=0

for i in xrange(1,101):
    rects=[]
    ptr=ptr+1
    bboxNum=data[ptr]
    for j in xrange(bboxNum):
        rects.append( (data[ptr+1],data[ptr+2],data[ptr+3],data[ptr+4]) )
        ptr=ptr+4
    CPUbox.append(rects)
    ptr=ptr+1
    #print i,rects


#print data
##Loop this for 1,2,3,4,...,100.png
CPU.read()
for i in xrange(1,101):
    count=0
    lst=[]
    Path = 'D:/ToDo/research_santa_cruz/train/'+str(i)+'.png'
    image_float_size = 600.0
    image_int_size = int(image_float_size)
    color = [0,255,0]
    rectangle = False
    # Read the image and convert it into gray
    image = cv2.imread(Path)
    gray_image = image#cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    centerOfMass=[]
    for x,y,w,h in CPUbox[i]:
        cv2.rectangle(gray_image, (x,y), (x+w,y+h), (0,0,255),1)
        centerOfMass.append( (x,y,w,h,(int(x+w/2), int(y+h/2))) )
    
    
    # resize the image
    ration = image_float_size / gray_image.shape[1]
    dim = (image_int_size,int(gray_image.shape[0]*ration))
    resized = cv2.resize(gray_image, dim, interpolation = cv2.INTER_AREA)
    draw_image = resized.copy()
    
    #print ration
    # set window for the image
    cv2.namedWindow('window')
    
    # mouse callback
    cv2.setMouseCallback('window',on_event)
    flag=0
    
    start = time.time()
    while True:
        cv2.imshow('window', draw_image)
        ch = 0xFF & cv2.waitKey(1)
        if ch == 27:
            elapsed = time.time()-start   
            print elapsed
            out.write(str(i)+' '+str(count)+' '+str(elapsed))
            for x,y,w,h in lst:
                out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            out.write('\n')
            flag=1
            break
        if ch == 13:
            elapsed = time.time()-start
            out.write(str(i)+' '+str(count)+' '+str(round(elapsed,3)))
            for x,y,w,h in lst:
                out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            out.write('\n')
            break
    
    if flag==1:
        break
    
cv2.destroyAllWindows()
out.close()