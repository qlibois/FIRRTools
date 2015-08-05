# -*- coding: utf-8 -*-

import Toolbox
import glob
from pylab import *
import os
from datetime import timedelta,datetime
from FirrSequence import FirrSequence

filtres_order = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']

class FirrSeries():
    """Calculations over a complete series of FIRR measurements"""  
    def __init__(self,folder,start_meas=datetime(2000,1,1),end_meas=datetime(2100,1,1)):    
        self.name = folder 
        sequences = glob.glob("%s/*"%self.name) 
        sequences = [s for s in sequences if os.path.isdir(s)]
        sequences.sort()  
        print sequences    
        all_dates = []
        for s in sequences:
            all_dates+=[Toolbox.get_time_seq(s)]
        start,end = searchsorted(all_dates,[start_meas,end_meas])    
        self.sequences = sequences[start:end]
        self.get_time_dir()
        self.start_date = Toolbox.get_time_seq(self.sequences[0]) 

    def get_time_dir(self):
        sd = self.name.rfind("201")
        self.date = self.name[sd:sd+10]            

    def get_temperature(self):   
        """ms since first measurement of the sequence"""  
        all_temp = []
        all_time = []
        for seq in self.sequences:
            if "Temperature.txt" in os.listdir(a):
                t = seq.get_time_seq()
                ms = t-self.start   
                data = genfromtxt("%s/Temperature.txt"%a,delimiter=",",skip_header=1,skip_footer=1,usecols = (0,9,17,19,21,23,25,27,29,31,33))                               
                all_time+= [self.start+timedelta(seconds=1e-3*d+ms.total_seconds()) for d in  data[:,0]]
                all_temp+= list(data[:,1:])
                
        self.temp_time = all_time
        self.temperature = array(all_temp)        
        
    def get_radiance(self,filtres_bt,npos=10,method="next",save=False):          
        good_seq=[s for s in self.sequences if "Temperature.txt" in os.listdir(s) and size(glob.glob("%s/*.raw"%s))%npos==0]      
        bt=[]  
        radiance=[]
        time=[]
        
        if save:
            f=open("QuickLookData/brightness_temperature_%s.txt"%self.date,"w")
            f.write("Date {0}  \n".format(" ".join([fil for fil in filtres_order]))) 
            g=open("QuickLookData/Radiance_%s.txt"%self.date,"w")
            g.write("Date {0}  \n".format(" ".join([fil for fil in filtres_order]))) 
            
        for rr,a in enumerate(good_seq): 
            if method == "next":
                if rr==len(good_seq)-1:
                    next_seq = a
                else:    
                    next_seq = good_seq[rr+1]
            else:
                next_seq = a
                
            seq = FirrSequence(a,npos,next_seq)
            print "Sequence time",seq.date0
            nview=seq.npos-2              
            seq.get_radiance(filtres_bt,method="next",spav="all") 
#            print seq.real_timestamp[2:]
#            raw_input()
            time+=seq.real_timestamp[2:]
            bt+=[seq.all_bt[:,nv] for nv in range(nview)]
            radiance+=[seq.all_radiance[:,nv] for nv in range(nview)]
#            rad+=[seq.rad[:,nv] for nv in range(nview)]
            if save:
                for nv in range(nview):
                    f.write("%s %s \n"%(datetime.strftime(seq.real_timestamp[nv+2],"%Y-%m-%d_%H-%M-%S")," ".join([str(a) for a in seq.bt[:,nv]])))
                    g.write("%s %s \n"%(datetime.strftime(seq.real_timestamp[nv+2],"%Y-%m-%d_%H-%M-%S")," ".join([str(a) for a in seq.rad[:,nv]])))
        if save:
            f.close()
            g.close()
            
        self.bt_series = array(bt) 
        self.radiance_series = array(radiance)
        self.time_series = array(time)      
         
    def get_netd(self,filtres_netd,fpos=10):
        netd_seq = [x for x in self.seq if os.path.isdir(x) and "Temperature.txt" in os.listdir(x) and size(glob.glob("%s/*.raw"% x))%fpos==0]        
        netd_flight = []
        netd_time = []
        for k,a in enumerate(netd_seq):
            sequence=FirrSequence(a,fpos,"zou")    
            print sequence.date0
            netd_time+=[sequence.date0]
            sequence.get_netd(filtres_netd,showplot=False)
            netd_flight+= [sequence.netd]
            
        self.netd_flight = array(netd_flight)
        self.netd_time = netd_time
        
        
    def get_gps(self):
        name_gps=self.date[2:4]+self.date[5:7]+self.date[8:10]
        files=glob.glob("/media/quentin/LACIE SHARE/GPS/GPS+LW_%s*.dat"%name_gps)
        gps=open(files[0],"r")
        dates=[]
        altitude=[]
        latitude=[]
        longitude=[]
                
        for line in gps:
          zou=line.split(",")
          if line.startswith("2015"):
            day=zou[0]
            sec=zou[1]
            dates+=[datetime(int(day[0:4]),int(day[5:7]),int(day[8:10]),int(sec[:2]),int(sec[3:5]),int(sec[6:8]))]
            altitude+=[float(zou[2])]
            latitude+=[int(0.01*float(zou[3]))+(0.01*float(zou[3]))%1/0.60]
            longitude+=[-(int(0.01*float(zou[4]))+(0.01*float(zou[4]))%1/0.60)]
            
        self.gps_dates=dates
        self.gps_alt=array(altitude)
        self.gps_lat=array(latitude)
        self.gps_lon=array(longitude)