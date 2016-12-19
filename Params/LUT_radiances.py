from pylab import *
import os
import glob
from scipy.integrate import trapz,simps
import Toolbox

epsilon_wls = array([1,200])
epsilon = array([1,1])
Tpm = 300

filtres_ref=['open','F0007','F0008','F0009','F0034','F0035','F0036','F0010','F0011','F0014','KT19']
n=len(filtres_ref)

temp=linspace(51,350,540)
l=len(temp)    
LUT_radiances = zeros([l,n+1])
LUT_radiances[:,0] = temp[:]

for k,f in enumerate(filtres_ref):  
    print f
    for i,t in enumerate(temp):
        LUT_radiances[i,k+1]=Toolbox.radiance_BB(t,f,epsilon_wls,epsilon,278)        
  
savetxt("LUT_radiances_new.txt",LUT_radiances)        