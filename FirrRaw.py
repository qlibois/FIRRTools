# -*- coding: utf-8 -*-

from pylab import *
import Toolbox
import time
import os

local_path = os.path.dirname(os.path.abspath(__file__)) # get path to local directory
illuminated = list(loadtxt("%s/Params/illuminated_pixels.txt"%local_path)) # illuminated pixels

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

    def analyze(self,frame_number=1000,spav="None"):
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

        for k in range(min(frame_number,self.nframes)):
            t = np.fromfile(f, dtype=np.uint32,count=1) # frame timestamp  
            frame = array(np.fromfile(f, dtype=np.uint16,count=self.npixels)).astype(float) # values for all pixels, returned in a 1D array 
            
            if len(frame)==self.npixels: # prevent from keeping erroneous frames
                tms+= [int(t)]                
                if spav=="all": 
                    """average on all illuminated pixels, only one value is saved per frame but an array is created to keep consistency with other options"""
                    frame = mean(frame[illuminated])
                    data_1D+= [frame*ones(2)] 
                    
                if isinstance(spav, int): 
                    """spatial mooving average on a spav x spav square"""
                    data_1D+=[Toolbox.get_av(frame,spav)]
                                    
                else: 
                    """no spatial average"""
                    data_1D+=[frame] # append new frame to existing ones
                                 
        self.mean = mean(array(data_1D),axis=0) 
        self.std = std(array(data_1D),axis=0)
                
        if spav == "all":
            corr=where(self.std<5.)[0]  # identify eroneous pixels
           
        elif isinstance(spav, int): 
            corr = where(self.std<1.2)[0]  
            
        else: 
            corr = where(self.std<2.)
            
        if not corr.size:
            print self.name,"No correct pixels",self.std
            plot(array(data_1D))[0]
            show()

        self.all_tms = array(tms)
        self.tms = mean(tms)    
        self.correct_pixels = corr

    
