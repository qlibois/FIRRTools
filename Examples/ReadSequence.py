# -*- coding: utf-8 -*-

from pylab import *
from FirrSequence import FirrSequence
import Toolbox

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

"""read a whole sequence and display radiance and brightness temperatures"""

filtres=['F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014']
all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
list_filters=[1,2,3,4,5,6,7,8,9]
labs=["open","10-12$\mu$m","12-14$\mu$m","17-18.5$\mu$m","22.5-27.5$\mu$m","7.9-9.5$\mu$m","20.5-22.5$\mu$m","18.5-20.5$\mu$m","17.25-19.75$\mu$m","30-50$\mu$m","blank"]
wls=array([0,11,13,17.75,25,8.7,21.5,19.5,18.5,40,0])
colors=["gold","red","blue","black","orange","yellow","cyan","green","Chartreuse","LightBlue"]


sequence = "Data/2015-07-30_14-23-46.0230" # Slow sequence AHNZ
seq_data = FirrSequence(sequence,10,sequence)
    
seq_data.get_bt(filtres,method="next",spav="all")
radiances = seq_data.rad[:,0]

"""Figure"""
fig,ax = subplots(1,1,figsize=(12,8))
fig.subplots_adjust(bottom=0.15)

for k in range(1,10):
    ax.plot(wls[k],radiances[k],"o",color=colors[k])

ax.set_xlim(0,50)
ax.grid()
ax.set_xlabel("Wavelength ($\mu$m)",size=20)
ax.set_ylabel("Radiance (W~m$^{-2}$~sr$^{-1}$)",size=20)
show()

  
   
    

