# -*- coding: utf-8 -*-

from pylab import *
from scipy import ndimage
from datetime import datetime
import os

local_path=os.path.dirname(os.path.abspath(__file__))

"""Look up table to convert radiance into brightness temperature"""
LUT_radiances=loadtxt("%s/Params/LUT_radiances.txt"%local_path)
temp_ref=LUT_radiances[:,0] 
rad_ref=LUT_radiances[:,1:]
filtres_lut=['open','F0007','F0008','F0009','F0034','F0035','F0036','F0010','F0011','F0014','blank']

def get_time_dir(directory):
    tirets = directory.rfind("201")
    return directory[tirets:tirets+10]
    
def get_time_seq(sequence):
    return datetime.strptime(sequence[-24:-5],"%Y-%m-%d_%H-%M-%S")    
    
def get_av(data,n):  
    data_2D = data.reshape(60,80)
    nav = (1+2*n)
    data_spav = ndimage.filters.uniform_filter(data,size=nav,mode="constant")
        
    return ravel(data_spav)        
    
"""Return transmitted radiance emitted by a blackbody (emissivity can be specified) in a given band""" 
"""Constants for Planck function"""
h=6.62e-34
c=3e8
kb=1.38e-23
def radiance(temp,filtre,epsilon_wls,epsilon,Tpm):
    if filtre=='open':        
        wls=1e-6*linspace(1,100,250)
        trans=100
        
    elif filtre=='blank':       
        wls=1e-6*linspace(1,100,250) 
        trans=zeros_like(wls)
        
    else:     
        data=loadtxt("%s/Params/Transmittance/%s.dat"%(local_path,filtre),skiprows=1)    
        wls=1e-6*data[:,0]
        trans=maximum(data[:,1],0)
        
    new_em=interp(wls,1e-6*epsilon_wls,epsilon)   
    # Accounting for radiation at Tpm reflected by BB 
    planck=2*h*c**2/wls**5*(new_em*1./(exp(h*c/(wls*kb*(temp)))-1)+(1-new_em)*1./(exp(h*c/(wls*kb*(Tpm)))-1))*trans*0.01
    
    return trapz(planck,wls)  
    
"""Return brightness temperature corresponding to radiance"""    
def find_temp_planck(rad,filtre,epsilon=1):
    j=filtres_lut.index(filtre)
    return interp(rad/epsilon,rad_ref[:,j],temp_ref)
    
def get_calib(amb1,hot,scene,amb2,thot,tscene,tamb2,Tamb1,Thot,Tamb2,filtre,emiss_wls,emiss,Tpma1,Tpmh,Tpma2):
    """Return 2D map of gain, offset, radiance and bt   
       amb=B0+G*Lamb 
       hot=B0+r*t1+G*Lhot
       amb2=B0+r*t2+G*Lamb2 
       r accounts for background linear variation"""
       
    # solving linear sysem to get B0, r, G   
    Lamb1=radiance(Tamb1+273.16,filtre,emiss_wls,emiss,Tpma1+273.16)
    Lhot=radiance(Thot+273.16,filtre,emiss_wls,emiss,Tpmh+273.16)
    Lamb2=radiance(Tamb2+273.16,filtre,emiss_wls,emiss,Tpma2+273.16)

    if tamb2 == 0: # no calibration with next
       G = (hot-amb1)/(Lhot-Lamb1)
       
    else:
       G = (tamb2*(hot-amb1)-thot*(amb2-amb1))/(tamb2*(Lhot-Lamb1)-thot*(Lamb2-Lamb1))
   
    B0 = amb1-G*Lamb1
    r = (hot-B0-G*Lhot)/thot
    scene=scene[:,:]
    ncorr=size(hot)
        
    #---------------------------------

    nview=shape(scene)[0]      
    bt=zeros([nview,ncorr])
    Lscene=zeros([nview,ncorr])
  
    # Calibration for all scene measurements and all valid pixels
    for nv in range(nview):
        correct_pixels=where(amb1[0]*hot[0]*scene[nv]*amb2[0]!=0)                
        Lscene[nv,:]=(scene[nv,:]-B0-r*tscene[nv])/G
        bt[nv,correct_pixels]=find_temp_planck(Lscene[nv,:],filtre)[correct_pixels]
#        if filtre=="F0008":
#            plot([Lamb1,Lhot,Lscene[nv,0]],[amb1,hot,scene[nv]],"o-")
#            show()         	
    
    return G,B0,Lscene,bt 
