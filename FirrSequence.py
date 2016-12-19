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
filters_positions_1=['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
filters_positions_2=['open','F0008','F0009','F0034','F0011','F0007','open','F0035','F0010','F0014','open','open','open','F0036','blank','open','open']
filters_positions_3 = ['F0011','open','F0007','open','F0036','F0035','open','open','F0010','F0014','blank','open','F0008','open','F0009','F0034','open']
filters_positions_4=['F0011','F0007','F0036','F0035','F0010','F0014','F0008','F0009','F0034','open','open','blank','open','open','blank','open','open']


"""Mask non-illuminated pixels for calculations"""
local_path = os.path.dirname(os.path.abspath(__file__)) # get path to local directory
#illuminated = list(loadtxt("%s/Params/illuminated_pixels_193.txt"%local_path)) # illuminated pixels
#non_illuminated = list(loadtxt("%s/Params/non_illuminated_pixels_193.txt"%local_path)) # illuminated pixels
#mask_illuminated = [k not in illuminated for k in range(4800)]
#unused = [k for k in range(4800) if k not in illuminated]

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
        temp_file = glob.glob("%s/*Temperature.txt"%folder)[0]                   
        cols=loadtxt(temp_file,delimiter=",",skiprows=1,usecols = (0,9,17,21,23,29)) # Read temperature records
        self.temp_tms = cols[:,0]
        self.temp_hbb = cols[:,1]
        self.temp_abb = cols[:,2]  
        self.temp_fw = cols[:,3] # filter wheel temperature needed for calibration
        self.temp_pm = cols[:,4] # pointing mirror temperature needed for calibration
        self.files = sorted(glob.glob("%s/*.raw"% self.folder)) # sorted raw files of the sequence
        self.filter_pos = filter_pos # number of filters used
        self.npos = size(self.files)/filter_pos # number of mirror positions used
        self.date0 = self.get_time_seq() # absolute timestamp of folder read in the name
        
        if self.date0>datetime(2015,2,20):
            self.filters_positions = filters_positions_4
            
        if self.date0>datetime(2015,12,9):
            self.filters_positions = filters_positions_3
            
        elif self.date0>datetime(2015,10,26):
            self.filters_positions = filters_positions_2
            
        else:
            self.filters_positions = filters_positions_1
               
        self.next=next_folder # use next folder to compute calibration in case of temperature variations
        if  illuminated_pixels == 1:
            self.illuminated = [3570]
            self.non_illuminated = [770]
        else:    
            self.illuminated = list(loadtxt("%s/Params/illuminated_pixels_%s_%s.txt"%(local_path,detector,illuminated_pixels))) # illuminated pixels
            self.non_illuminated = list(loadtxt("%s/Params/non_illuminated_pixels_%s_%s.txt"%(local_path,detector,illuminated_pixels))) # illuminated pixels
        self.unused = [k for k in range(4800) if k not in self.illuminated]     
        self.nframes = nframes
        self.detector=detector
        self.illuminated_pixels=illuminated_pixels

    def organized(self,spav="fast",non_ill=1):
        """ Sort all raw data in a 11 x npos array
            structure of all_mean = AH then ZZZ or NN or NZ for instance 
            mirror positions : ["N","Z","A","H"] """
              
        if spav == "fast" or spav == "all":
            npix = 2
            
        elif spav == "selected" or spav == "check":
            npix = len(self.illuminated)
        
        else:
            npix = 4800
          
        all_mean = zeros([17,self.npos,npix])   # all mean frames from raw files are stored in all_mean (11 filter wheel positions, npos pointing mirror positions)
        all_std = zeros([17,self.npos,npix])    # all std from raw files are stored in all_std (11 filter wheel positions, npos pointing mirror positions
        all_tms = zeros([17,self.npos])         # relative timestamp of each raw file (average through all frames)
        real_tms = []                           # absolute timestamp of each mirror position (when filter wheel in position 5)                      
        counter_filters = zeros([17])           # number of scene positions already accounted for for each filter
        
        for fichier in self.files:              
            raw_data = FirrRaw(fichier) 
            nf = min(raw_data.nframes,self.nframes)
            raw_data.analyze(nf,spav=spav,illuminated=self.illuminated,non_illuminated=self.non_illuminated,non_ill=non_ill)
            
            if raw_data.good: # do not read ill files   
                
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
           
            if raw_data.mpos == 0 or raw_data.mpos == 1: # even if bad file
                counter_filters[raw_data.fpos-1]+=1 
                
        for np in range(self.npos):
            real_tms+=[self.date0+timedelta(seconds=1e-3*all_tms[5,np])] # 5 to be in the middle of the sequence                       
                                              
        if spav == "check":
            all_mean_true = zeros([17,self.npos,2])   
            all_std_true = zeros([17,self.npos,2])    
            
            for nv in range(2):
                for k in range(17):
                    all_mean_true[k,nv,:] = mean(all_mean[k,nv,:])*ones(2)
                    all_std_true[k,nv,:] = mean(all_std[k,nv,:])*ones(2)
            
            for nv in range(2,self.npos):
                for k in range(17):
                    corr = where(all_mean[k,nv,:]*all_mean[k,0,:]!=0)[0]
#                    if corr.size:
#                        print std(all_mean[k,nv,corr]-all_mean[k,0,corr])/amax(all_mean[k,nv,corr]-all_mean[k,0,corr]) ; raw_input()
                    if corr.size and std(all_mean[k,nv,corr]-all_mean[k,0,corr])<2.3:
                        all_mean_true[k,nv,:] = mean(all_mean[k,nv,:])*ones(2)
                        all_std_true[k,nv,:] = mean(all_std[k,nv,:])*ones(2)
                   
                    else:
                        all_mean_true[k,nv,:] = zeros(2)
                        all_std_true[k,nv,:] = zeros(2)                             
                        
        if spav == "check":
            self.all_mean = ma.masked_equal(all_mean_true,0)
            self.all_std = all_std_true
        else:    
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
        print "organized"
        nview = self.npos-2   # number of scene measurements in a complete sequence
        
        if spav == "fast" or spav == "all" or spav == "check":
            all_mean = self.all_mean
            l = 2      
            
        elif spav == "selected":
            all_mean = self.all_mean
            l = len(self.illuminated)
            
        else: # keep all pixels for analysis
            all_mean = self.all_mean # calculations on all pixels only              
            l = 4800
                        
        all_tms = self.all_tms
        all_radiance = zeros([17,nview,l])  # Radiance (W/m2/sr) for each filter, several BT in a sequence if several nadir or zenith views     
        all_bt = zeros([17,nview,l])      # Brightness temperature for each filter,  
        offset = zeros([17,l])
        gain = zeros([17,l])       
        
        
        if method == "next": # use next folder to derive background variations
            next_seq = FirrSequence(self.next,self.filter_pos,next_folder="nocare",detector=self.detector,illuminated_pixels=self.illuminated_pixels)                     
            dtime = next_seq.get_time_seq()-self.get_time_seq() 
            dt = 1000*dtime.total_seconds() # in ms                     
            next_seq.organized(spav = spav,non_ill=non_ill)
            next_all_mean = next_seq.all_mean[:,:,:]                                                                   
            next_all_tms = next_seq.all_tms                      
                      
        for fil in list_filters:
            k = self.filters_positions.index(fil)
            i_abb1 = searchsorted(self.temp_tms,all_tms[k,0]) 
            Tamb1 = self.temp_abb[i_abb1]                # exact ABB temperature at measurement
            i_hbb1 = searchsorted(self.temp_tms,all_tms[k,1]) 
            i_scene = searchsorted(self.temp_tms,all_tms[k,2:])
            Thot1 = self.temp_hbb[i_hbb1]                  # exact HBB temperature at measurement
            Tpma1 = self.temp_pm[i_abb1]                 # pointing mirror temperature at ABB measurement
            Tpmh1 = self.temp_pm[i_hbb1]                   # pointing mirror temperature at HBB measurement
            Tpms = self.temp_pm[i_scene]
            
            thot1 = all_tms[k,1]
            tamb1 = all_tms[k,0]-thot1            
            tscene = all_tms[k,2:,None]-thot1
            amb1 = all_mean[k,0,:]
            hot1 = all_mean[k,1,:]
            scene = all_mean[k,2:,:]
            
            if method == "next":
                i_abb2 = searchsorted(next_seq.temp_tms,next_all_tms[k,0]) 
                Tamb2 = next_seq.temp_abb[i_abb2]            # exact ABB temperature for next sequence calibration
                Tpma2 = next_seq.temp_pm[i_abb2]             # pointing mirror temperature at next ABB measurement
                tamb2 = dt + next_all_tms[k,0]-thot1        # time after first ambient measurement
                amb2 = next_all_mean[k,0,:]  
                
                i_hbb2 = searchsorted(next_seq.temp_tms,next_all_tms[k,1]) 
                Thot2 = next_seq.temp_hbb[i_hbb2]            # exact ABB temperature for next sequence calibration
                Tpmh2 = next_seq.temp_pm[i_hbb2]             # pointing mirror temperature at next ABB measurement
                thot2 = dt + next_all_tms[k,1]-thot1         # time after first ambient measurement
                hot2 = next_all_mean[k,1,:]  
                
            else: # no interpolation in this case                
                Tamb2 = Tamb1
                Tpma2 = Tpma1
                tamb2 = tamb1 
                amb2 = amb1  
                
                Thot2 = Thot1
                Tpmh2 = Tpmh1
                thot2 = thot1 
                hot2 = hot1  
                
               
            # Calibration : S = B0 + G * rad_scene   
            G,B0,rad_scene,bt = Toolbox.get_calib(amb1,hot1,scene,amb2,hot2,tamb1,tscene,tamb2,thot2,Tamb1,Thot1,Tamb2,Thot2,fil,emiss_wls,emiss,Tpma1,Tpmh1,Tpms,Tpma2,Tpmh2)               
            all_bt[k,:,:] = bt 
                       
            all_radiance[k,:,:]=rad_scene
            offset[k,:] = B0
            gain[k,:] = G      
            
#            plot(ma.masked_equal(bt[0,:],0)-273.15,ma.masked_equal(B0,0),"bo")
#            show()
#            plot(ma.masked_equal(bt[0,:],0)-273.15,"bo")
#            if fil == "F0008":
#                for j in range(nview):
#                    rad_scene[j,self.unused] = 0
#                    imshow(bt[j,:].reshape(60,80),vmin=298,vmax=300)
#                    colorbar()
#                    show()
#                    plot(G[self.illuminated],ma.masked_equal(rad_scene[j,self.illuminated],0),"bo")
#                    ax = gca()
##                    ax2 = ax.twinx()
##                    ax2.plot(ma.masked_equal(,0),"ro")
#                    title("%s"%fil)
#                    show()
            
        if spav == "None" or isinstance(spav, int):
            self.all_bt = ma.median(ma.masked_equal(all_bt[:,:,self.illuminated],0),axis=2)             # contains 0 where not calculated  
            self.all_radiance = ma.median(ma.masked_equal(all_radiance[:,:,self.illuminated],0),axis=2) # moyenne spatiale des radiances
            self.offset = offset[:,self.illuminated]
            self.gain = gain[:,self.illuminated]
            
        else:    
            self.all_bt = ma.median(ma.masked_equal(all_bt,0),axis=2)             # contains 0 where not calculated  
            self.all_radiance = ma.median(ma.masked_equal(all_radiance,0),axis=2) # moyenne spatiale des radiances
            self.offset = offset
            self.gain = gain 
                       
    def get_netd(self,filters,spav='all',non_ill=1): 
        self.organized(spav=spav)
        mean_netd = zeros([17])
        mean_ner = zeros([17])
        mean_sigma = zeros([17])
        mean_sitf_temp = zeros([17])
        mean_sitf_rad = zeros([17])
        
        all_mean = self.all_mean
        all_std = self.all_std
        all_tms = self.all_tms
        
        for fil in filters:
            k = self.filters_positions.index(fil)  
            if spav == 'fast' or spav == "all":
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
                
                rad_hbb = Toolbox.radiance_BB(self.temp_hbb[i_hbb]+273.15,fil,emiss_wls,emiss,self.temp_pm[i_hbb])
                rad_abb = Toolbox.radiance_BB(self.temp_abb[i_abb]+273.15,fil,emiss_wls,emiss,self.temp_pm[i_abb])
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
           