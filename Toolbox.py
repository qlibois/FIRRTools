# -*- coding: utf-8 -*-

from pylab import *
from scipy import ndimage
from datetime import datetime
import os
from numpy.linalg import solve,lstsq

local_path=os.path.dirname(os.path.abspath(__file__))

"""Look up table to convert radiance into brightness temperature"""
LUT_radiances=loadtxt("%s/Params/LUT_radiances_new.txt"%local_path)
temp_ref=LUT_radiances[:,0] 
rad_ref=LUT_radiances[:,1:]
filtres_lut=['open','F0007','F0008','F0009','F0034','F0035','F0036','F0010','F0011','F0014','KT19','blank']

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
h = 6.626070e-34 # important to have accurate values otherwise bias in brightness temperatures
c = 2.99792e8
kb = 1.380648e-23
def radiance_BB(temp,filtre,epsilon_wls,epsilon,Tpm):
    if filtre=='open':        
        wls=1e-6*linspace(1,200,500)
        trans = 1
        
    elif filtre=='blank':       
        wls=1e-6*linspace(1,200,500) 
        trans=zeros_like(wls)
        
    else:     
        data=loadtxt("%s/Params/Transmittance_new/%s.dat"%(local_path,filtre),skiprows=1)    
        wls = 1e-6*data[:,0]
        trans = maximum(data[:,1],0)
        trans = trans/max(trans)
        
    new_em = interp(wls,1e-6*epsilon_wls,epsilon) # emissivity BB  
    
    # Accounting for radiation at Tpm reflected by BB + radiation from PM (emissivity assumed equal to BB) -> factor 2
    planck = 2*h*c**2/wls**5*(new_em*1./(exp(h*c/(wls*kb*(temp)))-1)+(1-new_em)*1./(exp(h*c/(wls*kb*(Tpm)))-1))*trans
#    planck = planck*0.97 + 0.03 * radiance_PM(Tpm+273.15,filtre)
#    plot(1e6*wls,planck)
#    title(filtre)
#    xlim(0,50)
#    show()
    return trapz(planck,wls)  
    
def radiance_PM(Tpm,filtre):
    if filtre=='open':        
        wls=1e-6*linspace(1,200,500)
        trans = 1
        
    elif filtre=='blank':       
        wls=1e-6*linspace(1,200,500) 
        trans=zeros_like(wls)
        
    else:     
        data=loadtxt("%s/Params/Transmittance_new/%s.dat"%(local_path,filtre),skiprows=1)    
        wls=1e-6*data[:,0]
        trans=maximum(data[:,1],0)
        trans = trans/max(trans)
        
    #Accounting for radiation at Tpm reflected by BB + radiation from PM (emissivity assumed equal to BB) -> factor 2
    planck = 2*h*c**2/wls**5*1/(exp(h*c/(wls*kb*(Tpm)))-1)*trans

    return trapz(planck,wls)     
    
"""Return brightness temperature corresponding to radiance"""    
def find_temp_planck(rad,filtre,epsilon=1):
    j=filtres_lut.index(filtre)
    if j>=11:
        return 0
    else:    
        return interp(rad/epsilon,rad_ref[:,j],temp_ref)
    
def get_calib(amb1,hot1,scene,amb2,hot2,tamb1,tscene,tamb2,thot2,Tamb1,Thot1,Tamb2,Thot2,filtre,emiss_wls,emiss,Tpma1,Tpmh1,Tpms,Tpma2,Tpmh2):
    """Return 2D map of gain, offset, radiance and bt   
       amb=B0+G*Lamb 
       hot=B0+r*t1+G*Lhot
       amb2=B0+r*t2+G*Lamb2 
       r accounts for background linear variation"""
       
    # solving linear sysem to get B0, r, G   
    Lamb1 = radiance_BB(Tamb1+273.15,filtre,emiss_wls,emiss,Tpma1+273.15)# + 0.001 * radiance_PM(Tpma1+273.15,filtre) # temp in °C -> K
    Lhot1 = radiance_BB(Thot1+273.15,filtre,emiss_wls,emiss,Tpmh1+273.15)# + 0.001 * radiance_PM(Tpmh+273.15,filtre)
    Lamb2 = radiance_BB(Tamb2+273.15,filtre,emiss_wls,emiss,Tpma2+273.15) # + 0.001 * radiance_PM(Tpma2+273.15,filtre)
    Lhot2 = radiance_BB(Thot2+273.15,filtre,emiss_wls,emiss,Tpmh2+273.15)

#    if tamb2 == tamb1: # no calibration with next
#        G = (hot-amb1)/(Lhot-Lamb1)
#     
#    else:
#        G = (tamb2*(amb1-hot)-tamb1*(amb2-hot))/(tamb2*(Lamb1-Lhot)-tamb1*(Lamb2-Lhot))
#    
#    B0 = hot-G*Lhot
#    r = (amb1-B0-G*Lamb1)/tamb1
#    
#    print "standard"
#    print G,B0,r

    if tamb2 == tamb1: # no calibration with next
        G = (hot1-amb1)/(Lhot1-Lamb1)
        B0 = hot1-G*Lhot1
        r1 = (amb1-B0-G*Lamb1)/tamb1
        r2 = 0
       
    else:
        # 1) solve y = Ax to get G and r1
        y = array([amb1,hot1,amb2,hot2])
        A = array([[1,tamb1,Lamb1],[1,0,Lhot1],[1,tamb2,Lamb2],[1,thot2,Lhot2]])
        B0,r1,G = lstsq(A,y)[0]
        r2 = 0
        
#        raw_input()
#        r2 = 0
        
        # 2) solve y = Ax to get B0 nd r2
        
#        y = array([amb1,hot1,amb2,hot2])
#        A = array([[1,Tpma1-Tpmh1,Lamb1],[1,0,Lhot1],[1,Tpma2-Tpmh1,Lamb2]])#,[1,Tpmh2-Tpmh1,Lhot2]])
#        B0,r1,G = solve(A,y)
#        r2 = 0
        
#        
#        print "3 parameters"
#        print G,B0,r1
        
#        y = array([amb1-G*Lamb1-r1*tamb1,hot1-G*Lhot1,amb2-G*Lamb2-r1*tamb1,hot2-G*Lhot2-r1*thot2])
#        A = array([[1,Tpma1-Tpmh1],[1,0],[1,Tpma2-Tpmh1],[1,Tpmh2-Tpmh1]])        
#        B0,r2 = lstsq(A,y)[0]
        
#        
#        print "4 parameters"
#        print G,B0,r1,r2 
#        print r1,r2 
#        raw_input()
        
    ncorr = size(hot1)
        
    #---------------------------------

    nview = shape(scene)[0]      
    bt = zeros([nview,ncorr])
    Lscene = zeros([nview,ncorr])
  
    # Calibration for all scene measurements and all valid pixels
    for nv in range(nview):
        correct_pixels = where(amb1*hot1*scene[nv,:]*amb2!=0)[0]
#        Lscene[nv,correct_pixels] = ((scene[nv,:]-B0-r*tscene[nv])[correct_pixels]/G[correct_pixels] - 0.001 * radiance_PM(Tpms[nv]+273.15,filtre))/0.999
        Lscene[nv,correct_pixels] = (scene[nv,:]-B0-r1*tscene[nv])[correct_pixels]/G[correct_pixels]
#        Lscene[nv,correct_pixels] = (scene[nv,:]-B0-r1*tscene[nv]-r2*(Tpms[nv]))[correct_pixels]/G[correct_pixels]
#        Lscene[nv,correct_pixels] = (scene[nv,:]-B0-r1*(Tpms[nv]-Tpmh1))[correct_pixels]/G[correct_pixels]
        bt[nv,correct_pixels] = find_temp_planck(Lscene[nv,:],filtre)[correct_pixels]
       
    return G,B0,Lscene,bt 
