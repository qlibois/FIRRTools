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
wls=array([0,11,13,17.75,25,8.7,21.5,19.5,18.5,40,0])
wlup = array([0,12,14,18.5,27.5,9.5,22.5,20.5,19.75,50])/50
wldown = array([0,10.,12.,17.,22.5,7.9,20.5,18.5,17.25,30])/50

series = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2"
data = FirrSeries(series)

npos = 10
all_sitf0= zeros([10,17])

for s,seq in enumerate(data.sequences[10:20]):      
    print seq
    sequence = FirrSequence(seq,npos,seq,illuminated_pixels=193,nframes=120)   
    sequence.get_netd(ordered_filters,spav='fast',non_ill=1)
    all_sitf0[s,:] = sequence.sitf_rad 
    
all_sitf = mean(all_sitf0,axis=0)    
    
fig = figure(12,figsize=(13,7))  
fig.subplots_adjust(bottom=0.12)  
ax = gca()        
for fil in ordered_filters:
    k = all_filters.index(fil)
    axhline(y=all_sitf[k],xmin=wldown[k],xmax=wlup[k],linewidth=2,color=colors[k])
    plot(wls[k],all_sitf[k],marker="o",linestyle="",markersize=8,mew=1.,mfc=colors[k],mec="k",color=colors[k])
    
    
xlabel(r"Wavelength ($\mu$m)",size=24)    
ylabel(r"Gain (counts W$^{-1}$~m$^{2}$~sr$)",size=24) 
#ylim(0,1.6)  
xlim(0,50)
grid() 
   
text(0.06,0.05,"(b)",fontsize=22,transform=ax.transAxes) 
fig.savefig("/home/quentin/Papiers/Libois2015_FIRR/Figures/SiTF.pdf",dpi=300,format="pdf")
#fig.savefig("/home/quentin/Documents/Presentations/Figures/SiTF.jpg",dpi=300,format="jpg")

show() 