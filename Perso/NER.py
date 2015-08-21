# -*- coding: utf-8 -*-

from FirrSequence import FirrSequence
from FirrSeries import FirrSeries
from pylab import *
import matplotlib.dates as md
from glob import glob

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

series = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2"
data = FirrSeries(series)


#seq = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_21-59-17.0755"
#seqs = glob("/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_22*")
#seq = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-31_05-26-02.0030"
npos = 10
npix=[1,9,25,45,69,109,145,193,249,305]
      
all_sigma = zeros([len(npix),11])      
      
for m,np in enumerate(npix):     
    print np       
    if np==1:
        all_std0 = zeros([10,11])
        for s,seq in enumerate(data.sequences[10:20]):
            print seq
            sequence = FirrSequence(seq,npos,seq,nframes=120)
            sequence.organized(spav="None",non_ill=1)
            all_std = sequence.all_std
            for fil in ordered_filters:
                k = all_filters.index(fil)
                all_std0[s,k] = all_std[k,0,3492]
                
        for fil in ordered_filters:
            k = all_filters.index(fil)
            print mean(all_std0[:,k]) 
            all_sigma[m,k] = mean(all_std0[:,k])      
    else:    
        all_std0 = zeros([10,11])
        for s,seq in enumerate(data.sequences[10:20]):
            sequence = FirrSequence(seq,npos,seq,illuminated_pixels=np,nframes=120)
            sequence.organized(spav="fast",non_ill=1)
            all_std = sequence.all_std
            for fil in ordered_filters:
                k = all_filters.index(fil)
                all_std0[s,k] = all_std[k,0,0]
                
        for fil in ordered_filters:
            k = all_filters.index(fil)
            all_sigma[m,k] = mean(all_std0[:,k]) 
            
fig = figure(12,figsize=(12,6))            
for fil in ordered_filters:
    k = all_filters.index(fil)
    plot(npix,all_sigma[:,k],marker="o",linestyle="-",markersize=3,mew=1.,mfc=colors[k],mec="k",color=colors[k],label=labs[k])
    
xlabel("Number of illuminated pixels",size=20)    
ylabel("Counts standard deviation",size=20) 
ylim(0,1.6)  
xlim(0,320)
grid() 
legend(loc=0,numpoints=1)
show()    

fig.savefig("/home/quentin/Papiers/FIRR_AMT/Figures/NER.pdf",dpi=300,format="pdf")
