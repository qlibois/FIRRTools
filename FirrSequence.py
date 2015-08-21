# -*- coding: utf-8 -*-

from pylab import *
import glob
from datetime import datetime
import Toolbox
from FirrRaw import FirrRaw
from datetime import timedelta
import os
             
"""Filters order in LUT and in filter wheel"""
filters_lut=['open','F0007','F0008','F0009','F0034','F0035','F0036','F0010','F0011','F0014','blank']
filters_positions=['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']

"""Mask non-illuminated pixels for calculations"""
local_path = os.path.dirname(os.path.abspath(__file__)) # get path to local directory
illuminated = list(loadtxt("%s/Params/illuminated_pixels_193.txt"%local_path)) # illuminated pixels
non_illuminated = list(loadtxt("%s/Params/non_illuminated_pixels_193.txt"%local_path)) # illuminated pixels
mask_illuminated=[k not in illuminated for k in range(4800)]

"""LR Tech BB emissivity"""
em = loadtxt("%s/Params/emissivity.dat"%local_path) 
emiss_wls = em[:,0]
emiss = em[:,1] 
     
class FirrSequence():
    """ Characteristics of a FIRR sequence
        temp_tms: time from Temperature.txt
        temp_hbb: HBB temperature
        temp_abb: ABB temperature
        files= all raw files in sequence
        filter_pos: number of filters used
        npos: number of files per filter
        date0: timestamp according to sequence name
        next: following sequence for interpolation
        counts: ordered raw counts
        stds: ordered stds
        timestamp: ordered relative timestamps in ms
        real_timestamp: absolute time stamps in datetime
        bt: brightness temperatures
        rad: calibrated radiances
        offset: map of offset
        gain: map of gain
        netd: mean for correct pixels
        sitf: mean for correct pixels
        sigma: mean for correct pixels """
        
    def __init__(self,folder,filter_pos,next_folder,detector=4,illuminated_pixels = 193,nframes=1000): 
        "Initalize the FirrSequence object"
        self.folder = folder                     
        cols=loadtxt("%s/Temperature.txt"%folder,delimiter=",",skiprows=1,usecols = (0,9,17,29)) # Read temperature records
        self.temp_tms = cols[:,0]
        self.temp_hbb = cols[:,1]
        self.temp_abb = cols[:,2]  
        self.temp_pm = cols[:,3] # pointing mirror temperature needed for calibration
        self.files = sorted(glob.glob("%s/*.raw"% self.folder)) # sorted raw files of the sequence
        self.filter_pos = filter_pos # number of filters used
        self.npos = size(self.files)/filter_pos # number of mirror positions used
        self.date0 = self.get_time_seq() # absolute timestamp of folder read in the name
        self.next=next_folder # use next folder to compute calibration in case of temperature variations
        self.illuminated = list(loadtxt("%s/Params/illuminated_pixels_%s_%s.txt"%(local_path,detector,illuminated_pixels))) # illuminated pixels
        self.non_illuminated = list(loadtxt("%s/Params/non_illuminated_pixels_%s_%s.txt"%(local_path,detector,illuminated_pixels))) # illuminated pixels
        self.nframes = nframes
        self.detector=detector
        self.illuminated_pixels=illuminated_pixels

    def organized(self,spav="fast",non_ill=1):
        """ Sort all raw data in a 11 x npos array
            structure of all_mean = AH then ZZZ or NN or NZ for instance 
            mirror positions : ["N","Z","A","H"] """
            
        if spav == "fast":
            npix = 2
            
        else:
            npix = 4800
          
        all_mean = zeros([11,self.npos,npix])   # all mean frames from raw files are stored in all_mean (11 filter wheel positions, npos pointing mirror positions)
        all_std = zeros([11,self.npos,npix])    # all std from raw files are stored in all_std (11 filter wheel positions, npos pointing mirror positions
        all_tms = zeros([11,self.npos])         # relative timestamp of each raw file (average through all frames)
        real_tms = []                           # absolute timestamp of each mirror position (when filter wheel in position 5)        
        counter_filters = zeros([11])           # number of scene positions already accoiunted for for each filter
        
        for fichier in self.files:              
            raw_data = FirrRaw(fichier) 
            nf = min(raw_data.nframes,self.nframes)
            raw_data.analyze(nf,spav=spav,illuminated=self.illuminated,non_illuminated=self.non_illuminated,non_ill=non_ill)
#            print fichier,raw_data.good
#            if raw_data.good: # do not read ill files    
            correct_pixels = raw_data.correct_pixels
      
            if raw_data.mpos == 2 and all_mean[raw_data.fpos-1,0,:].all() == 0:               # keep only first calibration                 
                all_mean[raw_data.fpos-1,0,correct_pixels] = raw_data.mean[correct_pixels]
                all_std[raw_data.fpos-1,0,correct_pixels] = raw_data.std[correct_pixels]
                all_tms[raw_data.fpos-1,0] = raw_data.tms 
                
            elif raw_data.mpos == 3 and all_mean[raw_data.fpos-1,1,:].all() == 0:               # keep only first calibration
                all_mean[raw_data.fpos-1,1,correct_pixels] = raw_data.mean[correct_pixels]
                all_std[raw_data.fpos-1,1,correct_pixels] = raw_data.std[correct_pixels]
                all_tms[raw_data.fpos-1,1] = raw_data.tms  
                
            elif raw_data.mpos == 0 or raw_data.mpos == 1:  # nadir or zenith view
                scene = counter_filters[raw_data.fpos-1] + 2                                          
                all_mean[raw_data.fpos-1,scene,correct_pixels] = raw_data.mean[correct_pixels]
                all_std[raw_data.fpos-1,scene,correct_pixels] = raw_data.std[correct_pixels]
                all_tms[raw_data.fpos-1,scene] = raw_data.tms    
                counter_filters[raw_data.fpos-1]+=1 

                
        for np in range(self.npos):
            real_tms+=[self.date0+timedelta(seconds=1e-3*all_tms[5,np])]                       
          
        self.all_mean = ma.masked_equal(all_mean,0)
        self.all_std = all_std
        self.all_tms = all_tms
        self.real_timestamp = real_tms
        
    def get_time_seq(self):
        return datetime.strptime(self.folder[-24:-5],"%Y-%m-%d_%H-%M-%S")    
    
    def get_radiance(self,list_filters,method="next",spav="fast",non_ill=1): 
        """Compute calibration for all filters indicated, correcting if necessary for the temperature drift between BB and scene measurements
        method : "next" to use following sequence to interpolate background signal"""
        self.organized(spav=spav,non_ill=non_ill)
        nview = self.npos-2   # number of scene measurements in a complete sequence
        
        if spav == "fast":
            all_mean = self.all_mean
            l = 2      
            
        else:
            all_mean = self.all_mean[:,:,self.illuminated]-non_ill*self.all_mean[:,:,self.non_illuminated] # calculations on illuminated pixels only              
            l = len(self.illuminated)
            
        all_tms = self.all_tms
        all_radiance = zeros([11,nview,l])  # Radiance (W/m2/sr) for each filter, several BT in a sequence if several nadir or zenith views     
        all_bt = zeros([11,nview,l])      # Brightness temperature for each filter,  
        offset = zeros([11,l])
        gain = zeros([11,l])       
        
        if method == "next":
            next_seq = FirrSequence(self.next,self.filter_pos,"nocare",detector=self.detector,illuminated_pixels=self.illuminated_pixels)                     
            dtime = next_seq.get_time_seq()-self.get_time_seq() 
            dt = 1000*dtime.total_seconds() # in ms                     
            next_seq.organized(spav = spav,non_ill=non_ill)
            
            if spav == "fast":
                next_all_mean = next_seq.all_mean[:,:,:]
                
            else:
                next_all_mean = next_seq.all_mean[:,:,self.illuminated]-non_ill*next_seq.all_mean[:,:,self.non_illuminated]
                
            next_all_tms = next_seq.all_tms                      
                      
        for fil in list_filters:
            k = filters_positions.index(fil)
            i_abb1 = searchsorted(self.temp_tms,all_tms[k,0]) 
            Tamb1 = self.temp_abb[i_abb1]                # exact ABB temperature at measurement
            i_hbb = searchsorted(self.temp_tms,all_tms[k,1]) 
            Thot = self.temp_hbb[i_hbb]                  # exact HBB temperature at measurement
            Tpma1 = self.temp_pm[i_abb1]                 # pointing mirror temperature at ABB measurement
            Tpmh = self.temp_pm[i_hbb]                   # pointing mirror temperature at HBB measurement
            tamb1 = all_tms[k,0]
            thot = all_tms[k,1]-tamb1
            tscene = all_tms[k,2:,None]-tamb1
            amb1 = all_mean[k,0,:]
            hot = all_mean[k,1,:]
            scene = all_mean[k,2:,:]
            
            if method == "next":
                i_abb2 = searchsorted(next_seq.temp_tms,next_all_tms[k,0]) 
                Tamb2 = next_seq.temp_abb[i_abb2]            # exact ABB temperature for next sequence calibration
                Tpma2 = next_seq.temp_pm[i_abb2]             # pointing mirror temperature at next ABB measurement
                tamb2 = dt + next_all_tms[k,0]-tamb1             # time after first ambient measurement
                amb2 = next_all_mean[k,0,:]      
                
            else: # no interpolation in this case                
                Tamb2 = Tamb1
                Tpma2 = Tpma1
                tamb2 = tamb1 
                amb2 = amb1
                  
               
            # Calibration : S = B0 + G * rad_scene   
            G,B0,rad_scene,bt = Toolbox.get_calib(amb1,hot,scene,amb2,thot,tscene,tamb2,Tamb1,Thot,Tamb2,fil,emiss_wls,emiss,Tpma1,Tpmh,Tpma2)               
            all_bt[k,:,:] = bt 

            all_radiance[k,:,:]=rad_scene
            offset[k,:] = B0
            gain[k,:] = G      
                 
        self.all_bt = ma.masked_equal(ma.average(ma.masked_equal(all_bt,0),axis=2),0) # contains 0 where not calculated  
        self.all_radiance = ma.average(ma.masked_equal(all_radiance,0),axis=2) # moyenne spatiale des radiances
        self.offset = offset
        self.gain = gain 
                       
    def get_netd(self,filters,spav='all',non_ill=1): 
        self.organized(spav=spav)
        mean_netd = zeros([11])
        mean_ner = zeros([11])
        mean_sigma = zeros([11])
        mean_sitf_temp = zeros([11])
        mean_sitf_rad = zeros([11])
        
        all_mean = self.all_mean
        all_std = self.all_std
        all_tms = self.all_tms
        
        for fil in filters:
            k = filters_positions.index(fil)  
            if spav == 'all' or spav == 'fast':
                correct_pixels = [i for i in range(2) if all_mean[k,0,i]*all_mean[k,1,i]!=0] 
            else:    
                correct_pixels = [i for i in self.illuminated if all_mean[k,0,i]*all_mean[k,1,i]!=0] 
        
            if not array(correct_pixels).size: # anomalies on all pixels, then no calculations
                print "NO GOOD PIXELS"
                mean_netd[num]=0
                mean_sigma[num]=0
                mean_sitf[num]=0              
                
            else:                
                i_abb = searchsorted(self.temp_tms,all_tms[k,0])-1
                i_hbb = searchsorted(self.temp_tms,all_tms[k,1])-1
                
                sitf_temp = (all_mean[k,1,:] - all_mean[k,0,:])/(self.temp_hbb[i_hbb] - self.temp_abb[i_abb])  
                
                rad_hbb = Toolbox.radiance(self.temp_hbb[i_hbb]+273.15,fil,emiss_wls,emiss,self.temp_pm[i_hbb])
                rad_abb = Toolbox.radiance(self.temp_abb[i_abb]+273.15,fil,emiss_wls,emiss,self.temp_pm[i_abb])
                sitf_rad = (all_mean[k,1,:] - all_mean[k,0,:])/(rad_hbb - rad_abb) 
                                
                netd = abs(all_std[k,0,:]/sitf_temp)  
                ner = abs(all_std[k,0,:]/sitf_temp)
                
                mean_netd[k] = mean(netd[correct_pixels])  
                mean_ner[k] = mean(ner[correct_pixels])
                mean_sitf_temp[k] = mean(sitf_temp[correct_pixels])
                mean_sitf_rad[k] = mean(sitf_rad[correct_pixels])
                mean_sigma[k] = mean(all_std[k,0,correct_pixels])
                
        self.sigma = mean_sigma         
        self.netd = mean_netd
        self.ner = mean_ner
        self.sitf_temp = mean_sitf_temp
        self.sitf_rad = mean_sitf_rad
           