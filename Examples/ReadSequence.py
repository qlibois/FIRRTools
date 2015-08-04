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

filters = ['F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014']
filters_positions = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
list_filters = [filters_positions.index(f) for f in filters]
wls = array([0,11,13,17.75,25,8.7,21.5,19.5,18.5,40,0])
colors = ["gold","red","blue","black","orange","yellow","cyan","green","Chartreuse","LightBlue"]

sequence = "Data/2015-07-30_14-23-46.0230" # Slow sequence AHNZ
seq_data = FirrSequence(sequence,10,sequence)
    
seq_data.get_radiance(filters,method="next",spav="all")
radiances = seq_data.all_radiance[:,0]
bt = seq_data.all_bt[:,0]

"""Figure"""
fig,(ax1,ax2) = subplots(1,2,figsize=(18,8))
fig.subplots_adjust(bottom=0.15)

for k in list_filters:
    ax1.plot(wls[k],radiances[k],"o",color=colors[k])
    ax2.plot(wls[k],bt[k]-273.15,"o",color=colors[k])
    
ax1.set_xlim(0,50)
ax1.grid()
ax1.set_xlabel("Wavelength ($\mu$m)",size=20)
ax1.set_ylabel("Radiance (W~m$^{-2}$~sr$^{-1}$)",size=20)

ax2.set_xlim(0,50)
ax2.grid()
ax2.set_xlabel("Wavelength ($\mu$m)",size=20)
ax2.set_ylabel("Brightness temperature ($^{\circ}$C)",size=20)

show()

  
   
    

