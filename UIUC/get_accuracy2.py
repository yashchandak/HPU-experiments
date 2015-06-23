# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 23:21:21 2015

@author: yash
"""
import os
def get_accuracy(fileName, valid):
    CPU = open(fileName, 'r')
    out = open('foundLocations_HPU.txt', 'w')

    data=CPU.read().split()
    data=[item for item in data]
    
    bboxs = []
    ptr=0
    while ptr<len(data):  
        if valid[ptr/6]=='1':
            bboxs.append( [int(data[ptr]),int(data[ptr+1]),int(data[ptr+2]),int(data[ptr+3]),int(data[ptr+4]), int(data[ptr+5])] )
        ptr=ptr+6        
                
    bboxs.sort(key=lambda lst: lst[0]) 
    
    ptr=0
    for i in range(108):
        out.write(str(i)+':')
        while ptr<len(bboxs) and bboxs[ptr][0]==i:
            out.write(' ('+str(bboxs[ptr][1])+','+str(bboxs[ptr][2])+','+str(bboxs[ptr][3])+')')
            ptr = ptr +1
        out.write('\n') 
    out.close()
    

    os.system("java Evaluator_Scale trueLocations_Scale.txt foundLocations_HPU.txt")
    results = open('results.txt')
    results = results.read().split()
    results = [float(item) for item in results]
    
    #reults = (Recall, Precision, Fmeasure)
    return results

#string u gave me had only 203 digits instead of 217, I added 14 zeros in the end
#valid = '0000000000111111111111111111111111111111111111111111111101111111111111111111111111111111111111101111111111101111110111101011101001011000110000000000010000010000000000000010000001001000010010000000000000000001111111111'   
valid = '1111111111111111111111111111111111111111111111111111111101111111111111111111111111111111111111101111111111101111110111101011101001011000110000000000010000010000000000000010000001001000010010000000000000000000000000000'
print get_accuracy('conf_simp.txt', valid)
#in case o java not found error, set java path in environment and restart; http://stackoverflow.com/questions/15796855/java-is-not-recognized-as-an-internal-or-external-command
