# -*- coding: utf-8 -*-
"""
Created on Wed Feb 04 12:12:40 2015
@author: Quentin
"""

from pylab import *

x0=45-1
y0=51-1

m_size = 4800 # number of pixels 
illuminated=[]
non_illuminated=[]
zone=zeros([60,80])
non_zone=zeros([60,80])
for k in range(m_size):
    x=k/80 
    y=k%80   
    if (x-x0)**2+(y-y0)**2<6**2:
        zone[x,y]=1
        illuminated+=[k]
    elif (x-x0)**2+(y-y0)**2>20**2:
        non_zone[x,y]=1
        non_illuminated+=[k]    
        
imshow(zone)        
show()
        
savetxt("illuminated_pixels.txt",array(illuminated))        
savetxt("non_illuminated_pixels.txt",array(non_illuminated))   
