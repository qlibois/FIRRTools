# -*- coding: utf-8 -*-
"""
Created on Wed Feb 04 12:12:40 2015
@author: Quentin
"""

from pylab import *

detector = 4

if detector == 3:
    x0 = 44-1
    y0 = 53-1
    x1 = 10-1
    y1 = 53-1
    x1 = 10-1
    y1 = 53-1
    x1 = 10-1   # top left corner for non illuminated area
    y1 = 53-1

if detector == 4:
    x0 = 45-1
    y0 = 53-1
    x1 = 10-1
    y1 = 53-1
#    x1 = 10-1   # top left corner for non illuminated area
#    y1 = 10-1
    x1 = 10-1   # top right corner for non illuminated area
    y1 = 61-1 # 70 cool; 53 and 60 correct; 40 très proches MODTRAN mais moins jolis 63 closest in background
    
for radius in [2,3,4,5,6,7,8]:   
#for radius in [8]:     
    m_size = 4800 # number of pixels 
    illuminated=[]
    non_illuminated=[]
    zone=zeros([60,80])
    zone_linear=zeros([4800])
    non_zone=zeros([60,80])
    for k in range(m_size):
        x=k/80 
        y=k%80   
        if (x-x0)**2+(y-y0)**2<radius**2:
            zone[x,y]=1
            illuminated+=[k]
        elif (x-x1)**2+(y-y1)**2<radius**2:
            non_zone[x,y]=1
            non_illuminated+=[k]    
    
    print len(illuminated)
    zone_linear[illuminated]=1
#    imshow(reshape(non_zone,(60,80)))   
#    imshow(reshape(zone,(60,80)),interpolation='none')   
#    grid()
#    show()
            
    savetxt("illuminated_pixels_%s_%s.txt"%(detector,int(len(illuminated))),array(illuminated))        
    savetxt("non_illuminated_pixels_%s_%s.txt"%(detector,int(len(illuminated))),array(non_illuminated))   

print "done"