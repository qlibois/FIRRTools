# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 12:34:55 2015

@author: quentin
"""

from pylab import *


#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
#---------------------------

ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0010','F0036','F0011','F0014']
all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
labs=["open","10-12~$\mu$m","12-14~$\mu$m","17-18.5~$\mu$m","22.5-27.5~$\mu$m","7.9-9.5~$\mu$m","20.5-22.5~$\mu$m","18.5-20.5~$\mu$m","17.25-19.75~$\mu$m","30-50~$\mu$m","blank"]
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]

# F0010
old = loadtxt("../Params/Transmittance/F0010.dat",skiprows=1) 
i = searchsorted(old[:,0],23)
old[i:,1] = 0
savetxt("../Params/Transmittance_new/F0010.dat",old)

# F0007
old = loadtxt("../Params/Transmittance/F0007.dat",skiprows=1) 
i,j = searchsorted(old[:,0],[6,23])
old[:i,1] = 0
old[j:,1] = 0
savetxt("../Params/Transmittance_new/F0007.dat",old)

# F0011
old = loadtxt("../Params/Transmittance/F0011.dat",skiprows=1) 
i = searchsorted(old[:,0],30)
old[i:,1] = 0
savetxt("../Params/Transmittance_new/F0011.dat",old)

# F0036
old = loadtxt("../Params/Transmittance/F0036.dat",skiprows=1) 
i = searchsorted(old[:,0],23)
old[i:,1] = 0
savetxt("../Params/Transmittance_new/F0036.dat",old)

# F0014
old = loadtxt("../Params/Transmittance/F0014.dat",skiprows=1) 
i,j = searchsorted(old[:,0],[25,70])
old[:i,1] = 0
old[j:,1] = 0
savetxt("../Params/Transmittance_new/F0014.dat",old)

fig1 = figure(13,figsize=(12,7))

for filtre in ordered_filters:
    k = all_filters.index(filtre)
    data=loadtxt("../Params/Transmittance_new/%s.dat"%(filtre),skiprows=1)    
    wls=data[:,0]
    trans=maximum(data[:,1],1)
    trans=data[:,1]
    plot(wls,trans,color=colors[k],linewidth=1.5,label = labs[k],alpha=0.8)
    
legend(loc=0)
ylim(0,100)
xlim(0,150)
xlabel("Wavelength ($\mu$m)",size=20)
ylabel("Transmittance ($\%$)",size=20)
grid()

#fig1.savefig("/home/quentin/Papiers/FIRR_AMT/Figures/Filters.pdf",dpi=300,format="pdf")


show()    