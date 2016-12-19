# -*- coding: utf-8 -*-

from pylab import *
import Toolbox
import time
import os

local_path = os.path.dirname(os.path.abspath(__file__)) # get path to local directory
illuminated = list(loadtxt("%s/Params/illuminated_pixels_4_193.txt"%local_path)) # illuminated pixels
non_illuminated = list(loadtxt("%s/Params/non_illuminated_pixels_4_193.txt"%local_path)) # illuminated pixels

class FirrRaw():
    """Calculations over a single FIRR raw file"""  
    
    def __init__(self,name):  
        "Create a FirrRaw object and initiates with header information"
        self.name = name   # name 
        f=open(self.name,'rb') # open raw file
        header = np.fromfile(f, dtype=np.uint32,count=4) # 4 first 32bits integers are header [number of frames, number of pixels, filter wheel position, mirror position]
        self.nframes = header[0]
        self.npixels = header[1]
        self.fpos = header[2]
        self.mpos = header[3]   
        self.good = True    # quality stamp, default = good       

    def analyze(self,frame_number=10000,spav="None",illuminated=illuminated,non_illuminated=non_illuminated,non_ill=1):
        """Compute average frame and standard deviation
        frame_number: defines how many frames should be used (default is all frames ie 1000)
        spav: spatial average to be computed
          - "fast" = spatial average of the frame to get a single average pixel
          - "all" = same as fact but remove bad pixels before averaging 
          - integer n = spatial moving average with square (1+n)**2
          - selected = keep individual pixels but only illuminated area
          - "None" = no spatial average - keep all 4800 pixels
        """   
        
        f = open(self.name,'rb')    # open raw file    
        header = np.fromfile(f, dtype=np.uint32,count=4)
        access_table = np.fromfile(f, dtype=np.uint16,count=self.npixels)    # id of the used pixels on the 120 x 160 standard grid of the bolometer     
        tms = []              # timestamps of the frames
        data_1D = []          # list to save all illuminated frames

        for k in range(min(frame_number,self.nframes)):
            t = np.fromfile(f, dtype=np.uint32,count=1) # frame timestamp= ms since folder creation
            frame = array(np.fromfile(f, dtype=np.uint16,count=self.npixels)).astype(float) # values for all pixels, returned in a 1D array 
            
            if len(frame) == self.npixels: # prevent from keeping erroneous frames
                tms+= [int(t)]  
                # append new frame to existing ones               
                if spav == "fast": # like "all" without eliminating bad pixels before averaging
                    frame = mean(frame[illuminated]) - non_ill*mean(frame[non_illuminated]) # substract non-illuminated area
                    data_1D+=[frame*ones(2)] # size 2 to be handled like 4800 full frame                    
                                        
                elif isinstance(spav, int): 
                    """spatial moving average on a spav x spav square"""
                    data_1D+= [Toolbox.get_av(frame,spav)]
                  
                elif spav == "all" or spav == "selected" or spav == "check":
                    data_1D+=[frame[illuminated]-non_ill*frame[non_illuminated]] 
                    
                else: # ie spav = None
                    data_1D+=[frame]                                       
        
        if data_1D == []: # mark empty file to avoid reading in a sequence
            self.good = False 
            
        elif shape(data_1D)[0] == 1: # mark small file to avoid reading in a sequence
            self.good = False                                  
        
        data_1D = array(data_1D)
 
        self.std = std(data_1D,axis=0) 
        self.mean = mean(data_1D,axis=0) 
       
#        if spav == "None" and self.fpos == 10:
#            imshow(self.std.reshape(60,80))
#            colorbar()
#            show()

        # remove bad pixels from analysis 
#        print "self.std",self.std
#        raw_input()
        if spav == "fast":
            corr = where(self.std<2.3)[0]    # big average pixel
            
        elif spav == "check":
            corr = where(self.std<20)[0] 
        
        elif isinstance(spav, int): 
            corr = where(self.std<1.2)[0]  
                        
        else:    
            corr = where(self.std<2.)[0]    # individual pixels
         
        self.all_tms = array(tms)
        self.tms = mean(tms)    
        self.correct_pixels = corr   

        if not corr.size:
            print self.name[-15:],"No correct pixels" 
#            self.good = False   
        elif corr.size < len(self.mean)/2:
#            self.good = False   
            print self.name[-15:],"%s correct pixels"%corr.size
        
        if spav == "all":
#            mean_all = [i for i in range(shape(data_1D)[1]) if i in corr]
#            mean_all_ni = [i for i in range(shape(data_1D)[1]) if i in corr and i in non_illuminated]
            
            if corr.size:
                self.mean = median(self.mean[corr])*ones(2)
                self.std = median(self.std[corr])*ones(2)
                self.correct_pixels = [0,1]
                
            else:
                print self.name,"zou"
                self.mean =array([0,0])
                self.correct_pixels = []

