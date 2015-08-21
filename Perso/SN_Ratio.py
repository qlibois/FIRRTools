# -*- coding: utf-8 -*-

from FirrSequence import FirrSequence
from pylab import *
import matplotlib.dates as md

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
#--------------------------------------

ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0010','F0036','F0011','F0014']
all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
labs=["open","10-12~$\mu$m","12-14~$\mu$m","17-18.5~$\mu$m","22.5-27.5~$\mu$m","7.9-9.5~$\mu$m","20.5-22.5~$\mu$m","18.5-20.5~$\mu$m","17.25-19.75~$\mu$m","30-50~$\mu$m","blank"]
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue","pink"]

seq = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_21-59-17.0755"
#seq = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-31_05-26-02.0030"
npos = 10
nframes=[10,20,30,50,100,150,200]
      
all_ratio = zeros([len(nframes),11])      
      
for m,nf in enumerate(nframes):     
    print nf       
    
    sequence = FirrSequence(seq,npos,seq,nframes=nf)
    sequence.organized(spav="all",non_ill=1)
    all_std = sequence.all_std
    all_mean = sequence.all_mean
    for fil in ordered_filters:
        k = all_filters.index(fil)
        all_ratio[m,k] = all_std[k,0,0]/nf
    
fig = figure(12,figsize=(12,6))            
for fil in ordered_filters:
    k = all_filters.index(fil)
    plot(nframes,all_ratio[:,k],marker="o",linestyle="-",markersize=3,mew=1.,mfc=colors[k],mec="k",color=colors[k],label=labs[k])
    
xlabel("Number of frames",size=20)    
ylabel("Signal-to-noise ratio",size=20) 
#ylim(0,1.6)  
grid() 
legend(loc=0,numpoints=1)
show()    

fig.savefig("/home/quentin/Papiers/FIRR_AMT/Figures/SNR.pdf",dpi=300,format="pdf")
