# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 14:55:14 2015

@author: quentin
"""

from pylab import *
from Toolbox import radiance

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
# ----------------------------------------

LUT_radiances=loadtxt("../Params/LUT_radiances.txt")
temp_ref=LUT_radiances[:,0]
rad_ref=LUT_radiances[:,1:]

dtemp = array([0,0.1,0.2,0.5,1.,1.5,2.,3.,4.,5.,7.,10,])
l = len(dtemp)
temp = arange(-120,25,5)
n = len(temp)


"""Filters order for LUT and operation"""
filtres_lut=['F0007','F0008','F0009','F0034','F0035','F0036','F0010','F0011','F0014']
ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0010','F0036','F0011','F0014']
all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
labs=["open","10-12~$\mu$m","12-14~$\mu$m","17-18.5~$\mu$m","22.5-27.5~$\mu$m","7.9-9.5~$\mu$m","20.5-22.5~$\mu$m","18.5-20.5~$\mu$m","17.25-19.75~$\mu$m","30-50~$\mu$m","blank"]
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]

epsilon_wls = array([5,100])
epsilon = array([1,1])
Tpm = 50

netd = zeros([9,n])

for i,f in enumerate(ordered_filters):
    print f
    for j,t in enumerate(temp):
        diff = zeros([l])
        for k,d in enumerate(dtemp):
            diff[k] = radiance(273.15+t+d,f,epsilon_wls,epsilon,Tpm)-radiance(273.15+t,f,epsilon_wls,epsilon,Tpm)
            
        netd[i,j] = interp(0.01,diff,dtemp)   
    
fig=figure(5,figsize=(13,7))   
for i,f in enumerate(ordered_filters):
        r = all_filters.index(f)
        plot(temp,netd[i,:],label=labs[r],color=colors[r])
    
legend(loc=0) 
ylim(0,1.6) 
grid()
xlabel("Temperature ($^\circ$C)",size=20)
ylabel("Temperature difference ($^\circ$C)",size=20)  
   
fig.savefig("/home/quentin/Papiers/FIRR_AMT/Figures/Temperature_Sensitivity.pdf",format="pdf",dpi=300)

show() 