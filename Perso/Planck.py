# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 08:34:11 2015

@author: quentin
"""

from pylab import *
from Toolbox import radiance_BB

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'20'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=24) 
rc('ytick',labelsize=24)
#--------------------------------------

# Planck function for different temperatures

h=6.62e-34
c=3e8
kb=1.38e-23
wls = 1e-6*linspace(1,100,2000)
new_em = ones_like(wls) 
ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0036','F0011'] # increasing wl

colors = ["red","orange","green","blue"]

temp = -30+273.15
planck = 2*h*c**2/wls**5*new_em*1./(exp(h*c/(wls*kb*(temp)))-1)
print 0.02*trapz(planck,wls)

temp = -30+273.15+2
planck2 = 2*h*c**2/wls**5*new_em*1./(exp(h*c/(wls*kb*(temp)))-1)
print trapz(planck2,wls) - trapz(planck,wls)


for fil in ordered_filters:
    print fil,0.1*radiance_BB(temp,fil,wls,new_em,300)

fig = figure(12,figsize=(12,8))
for k,temp0 in enumerate([20,0,-20,-60]):
    temp = temp0+273.15
    planck=2*h*c**2/wls**5*new_em*1./(exp(h*c/(wls*kb*(temp)))-1)
    if k==0:
        m = max(planck)
    plot(1e6*wls,5*planck/m,color=colors[k],label=r"%s$^{\circ}$C"%temp0)
    
legend(loc=0) 
grid()
xlabel(r"Wavelength ($\mu$m)",size=25)   
ylabel(r"Radiance (AU)",size=25) 
ylim(0,5.5)
show()



#fig.savefig("/home/quentin/Documents/Presentations/Figures/Planck.jpg",dpi=300,format="jpg")