# -*- coding: utf-8 -*-

from FirrSequence import FirrSequence
import Toolbox
from pylab import *
from matplotlib.ticker import MultipleLocator

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
#--------------------------------------

"""LR Tech BB emissivity"""
em = loadtxt("../Params/emissivity.dat") 
emiss_wls = em[:,0]
emiss = em[:,1] 

illuminated = list(loadtxt("../Params/illuminated_pixels.txt"))
non_illuminated = list(loadtxt("../Params/non_illuminated_pixels.txt"))


seq = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_21-47-25.0678"
npos = 10
sequence = FirrSequence(seq,npos,seq)

filters = ["F0008"]
k = 1

sequence.organized(spav="None",non_ill=0)
all_tms = sequence.all_tms
all_mean = sequence.all_mean

i_abb1 = searchsorted(sequence.temp_tms,all_tms[k,0]) 
Tamb1 = sequence.temp_abb[i_abb1]                # exact ABB temperature at measurement
i_hbb = searchsorted(sequence.temp_tms,all_tms[k,1]) 
Thot = sequence.temp_hbb[i_hbb]                  # exact HBB temperature at measurement
Tpma1 = sequence.temp_pm[i_abb1]                 # pointing mirror temperature at ABB measurement
Tpmh = sequence.temp_pm[i_hbb]                   # pointing mirror temperature at HBB measurement
tamb1 = all_tms[k,0]
thot = all_tms[k,1]-tamb1
tscene = all_tms[k,2:,None]-tamb1
amb1 = all_mean[k,0,:]
hot = all_mean[k,1,:]
scene = all_mean[k,2:,:]
              
Tamb2 = Tamb1
Tpma2 = Tpma1
tamb2 = tamb1 
amb2 = amb1
       
G,B0,rad_scene,bt = Toolbox.get_calib(amb1,hot,scene,amb2,thot,tscene,tamb2,Tamb1,Thot,Tamb2,filters[0],emiss_wls,emiss,Tpma1,Tpmh,Tpma2)               

new_G = zeros([4800])
new_B0 = zeros([4800])

new_G[illuminated] = G[illuminated]
new_B0[illuminated] = B0[illuminated]
new_B0[non_illuminated] = B0[non_illuminated]

#new_G = G
#new_B0 = B0

fig,(ax1,ax2) = subplots(2,1,figsize=(8,10))
fig.subplots_adjust(bottom=0.1,left=0.05,right=0.95,hspace=0.3)

cs1 = ax1.imshow(reshape(new_G,(60,80)),vmin=-34,vmax=-31.5,cmap=cm.gist_rainbow,interpolation='none')
cs1.cmap.set_under('w')
cs1.cmap.set_over('w')
spacing = 1 # This can be your user specified spacing. 
minorLocator = MultipleLocator(spacing)
# Set minor tick locations.
ax1.yaxis.set_minor_locator(minorLocator)
ax1.xaxis.set_minor_locator(minorLocator)
# Set grid to use minor tick locations. 
ax1.grid(which = 'minor',linestyle="-",alpha=0.2)
ax1.set_title("Gain",size=20)
colorbar(cs1,shrink=1,ax = ax1)

cs2 = ax2.imshow(reshape(new_B0,(60,80)),vmin = 30000,vmax=34000,cmap=cm.gist_rainbow,interpolation='none')
cs2.cmap.set_under('w')
cs2.cmap.set_over('w')
spacing = 1 # This can be your user specified spacing. 
minorLocator = MultipleLocator(spacing)
# Set minor tick locations.
ax2.yaxis.set_minor_locator(minorLocator)
ax2.xaxis.set_minor_locator(minorLocator)
# Set grid to use minor tick locations. 
ax2.grid(which = 'minor',linestyle="-",alpha=0.2)
ax2.set_title("Background",size=20)
colorbar(cs2,shrink=1,ax = ax2)

fig.savefig("/home/quentin/Papiers/FIRR_AMT/Figures/Background_spatial.pdf",dpi=300,format="pdf")

show()

