# -*- coding: utf-8 -*-

from pylab import *
import Toolbox
import time
import os

local_path = os.path.dirname(os.path.abspath(__file__)) # get path to local directory
illuminated = list(loadtxt("%s/Params/illuminated_pixels_193.txt"%local_path)) # illuminated pixels
non_illuminated = list(loadtxt("%s/Params/non_illuminated_pixels_193.txt"%local_path)) # illuminated pixels

class FirrRaw():
    """Calculations over a single FIRR raw file"""  
    
    def __init__(self,name):  
        "Create ar FirrRaw object and initiates with header information"
        self.name = name   # name 
        f=open(self.name,'rb') # open raw file
        header = np.fromfile(f, dtype=np.uint32,count=4) # 4 first 32bits integers are header [number of frames, number of pixels, filter wheel position, mirror position]
        self.nframes = header[0]
        self.npixels = header[1]
        self.fpos = header[2]
        self.mpos = header[3]   
        self.good = True        

    def analyze(self,frame_number=1000,spav="None",illuminated=illuminated,non_illuminated=non_illuminated,non_ill=1):
        """Compute average frame and standard deviation
        frame_number: defines how many frames should be used (default is all frames)
        spav: spatial average to be computed
          - "all" to return a single average value for illuminated pixels
          - integer n to return spatial moving average with square (1+n)**2
          - nothing to compute no spatial average
        """   
        
        f = open(self.name,'rb') # open raw file    
        header = np.fromfile(f, dtype=np.uint32,count=4)
        access_table = np.fromfile(f, dtype=np.uint16,count=self.npixels) # id of the used pixels on the 120 x 160 standard grid of the bolometer     
        tms = []
        data_1D = []  # list to save all frames
        data_1D_non_ill = []
        for k in range(min(frame_number,self.nframes)):
            t = np.fromfile(f, dtype=np.uint32,count=1) # frame timestamp  
            frame = array(np.fromfile(f, dtype=np.uint16,count=self.npixels)).astype(float) # values for all pixels, returned in a 1D array 
            
            if len(frame) == self.npixels: # prevent from keeping erroneous frames
                tms+= [int(t)]      
                if spav == "fast": # like "all" without eliminating bad pixels before averaging
                    frame = mean(frame[illuminated] - non_ill*frame[non_illuminated])
                    data_1D+=[frame*ones(2)]
                                        
                elif isinstance(spav, int): 
                    """spatial mooving average on a spav x spav square"""
                    data_1D+= [Toolbox.get_av(frame,spav)]
                  
                else:
                    data_1D+=[frame] # append new frame to existing ones
                
        if data_1D == []: # mark bad file to avoid reading in a sequence
            self.good = False 
            
        elif shape(data_1D)[0] == 1: # mark bad file to avoid reading in a sequence
            self.good = False                                  
        
        data_1D = array(data_1D)
       
        self.std = std(data_1D,axis=0) 
        self.mean = mean(data_1D,axis=0)         

        # remove bad pixels from analysis 
        if spav == "fast":
            corr = where(self.std<1.)[0]
        
        elif isinstance(spav, int): 
            corr = where(self.std<1.2)[0]  
                        
        else:    
            corr = where(self.std<1.8)[0]
         
        if not corr.size:
            print self.name,"No correct pixels"            

        self.all_tms = array(tms)
        self.tms = mean(tms)    
        self.correct_pixels = corr

    
