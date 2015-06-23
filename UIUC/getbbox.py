# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 16:40:56 2015

@author: yash
"""

fileName = 'foundLocations_Scale_conf.txt'

CPU = open(fileName, 'r')

data=CPU.read().split()
data=[item for item in data]

bboxs = []
ptr=0
imgNo = 0

#bbox format = (imgNo, x, y, width, height, confidence, validity)
while ptr<len(data):
    ptr=ptr+1
    bboxNum=int(data[ptr])
    for j in xrange(bboxNum):
        bboxs.append( [imgNo,int(data[ptr+1]),int(data[ptr+2]),int(data[ptr+3]),int(data[ptr+4]), int(data[ptr+5]), 1] )
        ptr=ptr+5
    imgNo = imgNo + 1
    ptr=ptr+1

            
bboxs.sort(key=lambda lst: lst[5]) 


cc = open('update_conf.txt', 'w')
for bbox in bboxs:
    for item in bbox:
        cc.write(str(item)+' ')
    cc.write('\n')
    
CPU.close()
cc.close()