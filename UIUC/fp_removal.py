# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 12:57:19 2015

@author: yash


==========NOTE========

"""
import cv2, time, os
import numpy as np

cv2.namedWindow('display', 1)

"""'update_conf.txt contains all the CPU bboxs of the UIUC multi scale in the order of confidence """

#read the bboxs and their confidence values
conf=open('update_conf.txt', 'r')
data=conf.read().split()
data=[item for item in data]
conf.close()


#bbox format = (imgNo, x, y, width, height, confidence, validity)
bboxs = []
ptr=0
while ptr<len(data):    
    bboxs.append( [int(data[ptr]), int(data[ptr+1]),int(data[ptr+2]),int(data[ptr+3]),int(data[ptr+4]), int(data[ptr+5]), int(data[ptr+6])] )
    ptr=ptr+7
    
#bboxs (--already)sorted by confidence
#bboxs.sort(key=lambda lst: lst[5])   


#Remove false positives
i = 0
totaltime=0
timeFile = open('time.txt','a')

while i< len(bboxs):
    print 'bbox no: ', i
    imgNo = bboxs[i][0]
    count=0
    #lst=[]
    #Path = 'D:/ToDo/research_santa_cruz/train/'+str(imgNo)+'.png'
    Path = 'D:/ToDo/research_santa_cruz/car_classifier/CarData/TestImages_Scale/test-'+str(imgNo)+'.pgm'
    image_float_size = 600.0
    image_int_size = int(image_float_size)
    color = [0,255,0]
    #rectangle = False
    # Read the image and convert it into gray
    image = cv2.imread(Path)
    
    y,x, width, height = bboxs[i][1:5]
    #print x,y,width,height
    #gray_image = image[x:x+width,y:y+height]
    #print image.shape
    cv2.rectangle(image,(x,y),(x+width,y+height),(0,255,0))
    #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    
    # resize the image
    ration = image_float_size / image.shape[1]
    dim = (image_int_size,int(image.shape[0]*ration))
    resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    image = resized.copy()
    #print ration    
    # mouse callback
    flag=0
    
    start = time.time()
    paused = 0
    while True:
        cv2.imshow('display', image)
        ch = 0xFF & cv2.waitKey(1)
        if ch == 97:
            #press 'a' to reject
            elapsed = time.time()-start-paused
            print elapsed
            timeFile.write(str(elapsed)+'\n')
            totaltime = totaltime + elapsed
            bboxs[i][5] = max(3,int(bboxs[i][5]/2))
            bboxs[i][6] = bboxs[i][6] - 1
            break
        
        elif ch == 108:
            #press 'l' to accept
            elapsed = time.time()-start-paused 
            print elapsed
            timeFile.write(str(elapsed)+'\n')
            totaltime = totaltime + elapsed
            bboxs[i][5] = int(bboxs[i][5]*2)
            bboxs[i][6] = bboxs[i][6] + 1            
            break
        
        elif ch == 27:
            #press 'Esc' to force close
            print '====Forced exit===='
            elapsed = time.time()-start-paused 
            print elapsed
            totaltime = totaltime + elapsed
            #out.write(str(i)+' '+str(count)+' '+str(elapsed))
            #for x,y,w,h in lst:
                #out.write(' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h))
            # out.write('\n')
            if ch == 27:
                flag=1
            break
        
        
        elif ch==112:
            #press 'p' to pause
            print 'paused..',
            paused = time.time()
            
            while True:
                ch = cv2.waitKey(1)
                if ch ==112:    
                    paused = time.time() - paused
                    break
                
            print 'for total: ', paused        
    if flag:
        break
    i=i+1
    
timeFile.write('\n\n')
timeFile.close()

#sorting based on updated confidnce    
bboxs.sort(key=lambda lst: lst[5])    

#storing updated confidence
cc = open('update_conf.txt','w')
for bbox in bboxs:
    for item in bbox:
        cc.write(str(item)+' ')
    cc.write('\n')
cc.close()

"""add the false negative removal results here to bboxs"""

#sorting based on image number    
bboxs.sort(key=lambda lst: lst[0])    

#storing the intermediate results and evaluating accuracy measures
temp = open('foundLocations_HPU.txt', 'w')
fpr = open('fp_removed.txt','w')
ptr=0
for i in range(108):
    temp.write(str(i)+':')
    fpr.write(str(i)+' ')
    rects = []
    while ptr<len(bboxs) and bboxs[ptr][0]==i:
        if bboxs[ptr][6] < 1:
            #if majority have declined then reject the bbox
            ptr = ptr+1
            continue
        rects.append([bboxs[ptr][1],bboxs[ptr][2], bboxs[ptr][3], bboxs[ptr][4], bboxs[ptr][5]])
        temp.write(' ('+str(bboxs[ptr][1])+','+str(bboxs[ptr][2])+','+str(bboxs[ptr][3])+')')
        ptr = ptr +1
        
    fpr.write(str(len(rects)))
    for item in rects:
        fpr.write(' '+str(item[0])+' '+str(item[1])+' '+str(item[2])+' '+str(item[3])+' '+str(item[4]))
        
    fpr.write('\n')
    temp.write('\n')
fpr.close()
temp.close()


os.system("java Evaluator_Scale trueLocations_Scale.txt foundLocations_HPU.txt")
results = open('results.txt','r')
results = results.read().split()
results = [float(item) for item in results]

#cache the results
out=open('HpuResults.txt', 'a')
out.write(str(results[0])+ ' '+ str(results[1])+' '+ str(results[2]) +' '+ str(totaltime) + '\n\n')
out.close()



cv2.destroyAllWindows()
out.close()
    