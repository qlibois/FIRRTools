# -*- coding: utf-8 -*-

from pylab import *
import glob
from datetime import datetime
import Toolbox
from FirrRaw import FirrRaw
from datetime import timedelta
import os

                
"""Filters order for LUT and operation"""
filters_lut=['open','F0007','F0008','F0009','F0034','F0035','F0036','F0010','F0011','F0014','blank']
filters_positions=['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
mirror_positions=["N","Z","A","H"]

"""Mask non-illuminated pixels for calculations"""
local_path = os.path.dirname(os.path.abspath(__file__)) # get path to local directory
illuminated = list(loadtxt("%s/Params/illuminated_pixels.txt"%local_path)) # illuminated pixels
mask_illuminated=[k not in illuminated for k in range(4800)]
     
class FirrSequence:
    """Characteristics of a FIRR sequence
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
    sigma: mean for correct pixels"""
    
    
    def __init__(self,folder,filter_pos,next_folder):    
        self.folder = folder              
        """Read temperature records"""
        cols=loadtxt("%s/Temperature.txt"%folder,delimiter=",",skiprows=1,usecols = (0,9,17,29))
        self.temp_tms = cols[:,0]
        self.temp_hbb = cols[:,1]
        self.temp_abb = cols[:,2]  
        self.temp_pm = cols[:,3] # pointing mirror
        dd = glob.glob("%s/*.raw"% self.folder)
        dd.sort()
        self.files = dd
        self.filter_pos = filter_pos
        self.npos = size(self.files)/filter_pos
        self.date0 = self.get_time_seq() # absolute timestamp of folder
        self.next=next_folder

    def organized(self,number_of_frames=200,spav="all"):
        """ structure of outpout = AH then ZZZ or NN for instance """
        if spav == "all":
            all_outputs=zeros([11,self.npos,2])
            all_sigma=zeros([11,self.npos,2])
        else:    
            all_outputs=zeros([11,self.npos,4800])  # 11 filter wheel positions, n pointing mirror positions
            all_sigma=zeros([11,self.npos,4800])
        tms=zeros([11,self.npos])               # relative timestamp of each .raw file (average through all frames)
        real_tms=[]                             # absolute timestamp of each mirror position (when filter wheel in position 5)        
        for fichier in self.files:  
#            print "fichier",fichier
            raw_data=FirrRaw(fichier)
            raw_data.analyze(raw_data.nframes,spav=spav) # [filter number, mirror position, average tms, average counts, std]  
            correct_pixels=raw_data.correct_pixels
            
            if 1==1:#raw_data.nframes==number_of_frames: 
                 
                if raw_data.mpos == 2 and all_outputs[raw_data.fpos-1,0,:].all()==0:            # keeps only first calibration                 
                    all_outputs[raw_data.fpos-1,0,correct_pixels]=raw_data.mean[correct_pixels]
                    all_sigma[raw_data.fpos-1,0,correct_pixels]=raw_data.std[correct_pixels]
                    tms[raw_data.fpos-1,0]=raw_data.timestamp 
#                    print "ABB",raw_data.std[correct_pixels],raw_data.mean[correct_pixels]
                    
                elif raw_data.mpos==3 and all_outputs[raw_data.fpos-1,1,:].all()==0:                # keeps only first calibration
                    all_outputs[raw_data.fpos-1,1,correct_pixels]=raw_data.mean[correct_pixels]
                    all_sigma[raw_data.fpos-1,1,correct_pixels]=raw_data.std[correct_pixels]
                    tms[raw_data.fpos-1,1]=raw_data.timestamp 
#                    print "HBB",raw_data.std[correct_pixels],raw_data.mean[correct_pixels]   
                    
                elif raw_data.mpos==0 or raw_data.mpos==1:  # nadir or zenith view
                    nv=0
                    while all_outputs[raw_data.fpos-1,nv+2,:].any()!=0: 
                        nv+=1                     
    
                    all_outputs[raw_data.fpos-1,nv+2,correct_pixels]=raw_data.mean[correct_pixels]
                    all_sigma[raw_data.fpos-1,nv+2,correct_pixels]=raw_data.std[correct_pixels]
                    tms[raw_data.fpos-1,nv+2]=raw_data.timestamp
#                    print "NZ",raw_data.std[correct_pixels],raw_data.mean[correct_pixels]
                    
#                raw_input()  
        for np in range(self.npos):
            real_tms+=[self.date0+timedelta(seconds=1e-3*tms[5,np])]                          
          
        self.counts=all_outputs
        self.stds=all_sigma
        self.timestamp=tms
        self.real_timestamp=real_tms
        
    def get_time_seq(self):
        return datetime.strptime(self.folder[-24:-5],"%Y-%m-%d_%H-%M-%S")    
    
    def get_bt(self,list_filters,method="next",spav="all",krad=False): # method can be next or blank (blank not operational anymore)
        """ 0 : nadir , 1 : zenith ,  2 : ambient , 3 : hot """
        self.organized(spav=spav)
        nview=self.npos-2 # number of scene measurements in a complete sequence
        
        if spav == "all":
            all_outputs=self.counts
            l=2
        else:
            all_outputs=self.counts[:,:,[illuminated]] # calculations on illuminated pixels only  
            l=len(illuminated)
        tms=self.timestamp
        calib_outputs=zeros([11,nview,l])          # Tb for each filter, several Tb in a sequence if several nadir or zenith
        radiance=zeros([11,nview,l])
        offset=zeros([11,l])
        gain=zeros([11,l])       
        
        if method == "next":
            next_seq=FirrSequence(self.next,self.filter_pos,"nothing")
            dtime=Toolbox.get_time_seq(self.next)-Toolbox.get_time_seq(self.folder) # time lapse between 2 consecutive sequences
            dt=1000*dtime.total_seconds() # in ms
            if self.next == self.folder:
                if spav == "all":
                    next_outputs=self.counts[:,:,:]
                else:
                    next_outputs=self.counts[:,:,[illuminated]]
                next_tms=self.timestamp      
                
            else:    
                next_seq.organized(spav = spav)
                if spav == "all":
                    next_outputs=next_seq.counts[:,:,:]
                else:
                    next_outputs=next_seq.counts[:,:,[illuminated]]
                next_tms=next_seq.timestamp      
                
                      
        for fil in list_filters: # no calculations on blank
            k=filtres.index(fil)
            i_abb1 = searchsorted(self.temp_tms,tms[k,0]) # exact ABB temperature at measurement
            Tamb1 = self.temp_abb[i_abb1]
            i_hbb = searchsorted(self.temp_tms,tms[k,1]) # exact ABB temperature at measurement
            Thot = self.temp_hbb[i_hbb]
            Tpma1 = self.temp_pm[i_abb1]
            Tpmh = self.temp_pm[i_hbb]             
            tamb1 = tms[k,0]
            thot = tms[k,1]-tamb1
            tscene = tms[k,2:,None]-tamb1
            amb1 = all_outputs[k,0,:]
            hot = all_outputs[k,1,:]
            scene = all_outputs[k,2:,:]
            
            if spav=="all":
                if method=="blank":  
                    slope = (all_outputs[10,2,0]-all_outputs[10,0,0])/(tms[10,2]-tms[10,0])
                    offset_hot = slope*(tms[10,1]-tms[10,0])             
                    offset_scene=slope*(tms[10,2:,None]-tms[10,0,None])
                
                elif method=="next":  
                    i_abb2 = searchsorted(next_seq.temp_tms,next_tms[k,0]) # exact ABB temperature at next measurement
                    Tamb2 = next_seq.temp_abb[i_abb2]
                    Tpma2 = next_seq.temp_pm[i_abb2]
                    tamb2 = dt + next_tms[k,0]-tamb1 # time after first ambient measurement
                    amb2 = next_outputs[k,0,:]                                      
                    
            else:    
                # Slope of offset calculated with blank (filter position 10) - valid only for AHZ or AHN sequence
                if method=="blank":  
                    slope = (all_outputs[10,2,:]-all_outputs[10,0,:])/(tms[10,2]-tms[10,0])
                    slope = slope[0,:]
                    offset_hot = slope*(tms[10,1]-tms[10,0])             
                    offset_scene=slope*(tms[10,2:,None]-tms[10,0,None])
                    
                elif method=="next":         
                    i_abb2 = searchsorted(next_seq.temp_tms,next_tms[k,0]) # exact ABB temperature at next measurement
                    Tamb2 = next_seq.temp_abb[i_abb2]
                    Tpma2 = next_seq.temp_pm[i_abb2]
                    tamb2 = dt + next_tms[k,0]-tamb1 # time after first ambient measurement
                    amb2 = next_outputs[k,0,:] 
                    
#                    print "thot,tscene,tamb2",thot,tscene,tamb2
             
            em = loadtxt("%s/Params/emissivity.dat"%local_path) # BB emissivity
            emiss_wls = em[:,0]
            emiss = em[:,1]   
                         
            G,B0,Lscene,bt = Toolbox.get_calib(amb1,hot,scene,amb2,thot,tscene,tamb2,Tamb1,Thot,Tamb2,fil,emiss_wls,emiss,Tpma1,Tpmh,Tpma2)               
            calib_outputs[k,:,:] = bt 

            radiance[k,:,:]=Lscene
            offset[k,:] = B0
            gain[k,:] = G      
                 
        self.bt = mean(ma.masked_equal(calib_outputs,0),axis=2) # contains 0 where not calculated         
        self.rad = mean(ma.masked_equal(radiance,0),axis=2)
        self.offset = mean(offset,axis=1) 
#        self.offset = offset[:,35] 
        self.gain = mean(gain,axis=1) 
#        self.gain = gain[:,35] 
        
#        print "Brightness temperature",self.bt-273.15
               
        
    def get_netd(self,filters_id,number_of_frames=100,showplot=False): 
        self.organized(number_of_frames=number_of_frames)
        mean_netd=zeros([11])
        mean_sigma=zeros([11])
        mean_sitf=zeros([11])
        
        all_outputs=self.counts
        all_sigma=self.stds
        tms=self.timestamp
        
        i_abb=searchsorted(self.temp_tms,tms[:,0])-1
        i_hbb=searchsorted(self.temp_tms,tms[:,1])-1

        sitf=(all_outputs[:,1,:]-all_outputs[:,0,:])/(self.temp_hbb[i_hbb,None]-self.temp_abb[i_abb,None])       
        
        for k in filters_id:
            num=filtres.index(k)   
            correct_pixels=[i for i in illuminated if all_outputs[num,0,i]*all_outputs[num,1,i]!=0] 
        
            if correct_pixels==[]: #anomalies on all pixels, then no calculations
                print "NO GOOD PIXELS"
                mean_netd[num]=0
                mean_sigma[num]=0
                mean_sitf[num]=0              
                
            else:                         
                netd=abs(all_sigma[num,0,:]/sitf[num,:])     
                mean_netd[num]=mean(netd[correct_pixels])  
                mean_sitf[num]=mean(sitf[num,correct_pixels])
                mean_sigma[num]=mean(all_sigma[num,1,correct_pixels])
                
                if showplot: 
                    netd=ma.masked_array(netd,mask=mask_illuminated)
                    imshow(reshape(netd,(60,80)),vmin=-0.5,vmax=2)
                    colorbar()
                    title("%s"%filter_id)
                    show()    
            
        self.netd = mean_netd
        self.sitf = mean_sitf 
        self.sigma = mean_sigma    