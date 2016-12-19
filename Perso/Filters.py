# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 12:34:55 2015

@author: quentin
"""

from pylab import *
from matplotlib.patches import FancyArrow


#-------------Latex Style--------------
#rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('font',**{'family':'sans-serif','sans-serif':['Computer Modern Sans Serif'],'size':'20'})
rc('text', usetex=True)
#--------------------------------------

#mpl.rcParams['font.family'] = 'Cabin'
#mpl.rcParams['font.size'] = '14'
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{sansmath}',r'\sansmath']

rc('xtick',labelsize=24) 
rc('ytick',labelsize=24)
#---------------------------

ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0010','F0036','F0011','F0014']

all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
labs=["open","10-12~$\mu$m","12-14~$\mu$m","17-18.5~$\mu$m","22.5-27.5~$\mu$m","7.9-9.5~$\mu$m","20.5-22.5~$\mu$m","18.5-20.5~$\mu$m","17.25-19.75~$\mu$m","30-50~$\mu$m","blank"]
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]

fig1 = figure(13,figsize=(12,8))

# TOA 11 April
ax = gca()

toa = open("/data/quentin/MODTRAN/MODTRAN_5.4/Work/NETCARE/2015-04-11/Simuls/NETCARE_2015-04-11-1_cs_28.plt","rb")
data = genfromtxt(toa,skip_header=0,skip_footer=1)
wls = data[::-1,0]     # m
rad = data[::-1,1]*1e4  # rad en W cm-2 um-1 so *1e10 to get W m-2 m-1
    
ax.plot(wls,rad,"k-",lw=2) 
ax.axvline(x=15,color="red",lw=3)
ax.arrow(16,3,32,0,head_width=0.1,head_length=2,linestyle="-", ec='red',fc="red",lw=3)
ax.arrow(46,3,46,0,head_width=0.1,head_length=3,linestyle="--", ec='none',fc="red",lw=2)
Arrow(16,3,30,0,width=2,color="r")
ax.add_patch(FancyArrow(16,3,30,0,width=0.05,head_width=0.2,head_length=5,color="r",ls="--"))
ax.annotate('', xy=(50,3.), xytext=(16,3),arrowprops={'ls':'dashed','shrink':0.02,'color':"red",'width':10,'headwidth':20,'frac':2}, va='center')
ax.annotate('default arrow', xy=(0.35,0.3), xytext=(0.6,0.3),
ax.axhline(y=3,xmin=0.2,xmax=0.5,color="red",lw=2)
text(20,3.1,"Far-infrared (FIR)",size=24,color="red")
text(16,0.5,"15 $\mu$m",size=24,color="red")
ax.set_ylim(0,3.5)
ax2 = ax.twinx() 
ax.set_ylabel(r"Radiance (W m$^{-2}$ sr$^{-1}$ $\mu$m$^{-1}$)",size=26)

subplots_adjust(left=0.13,right=0.9)
for filtre in ordered_filters:
    k = all_filters.index(filtre)
    data=loadtxt("../Params/Transmittance_new/%s.dat"%(filtre),skiprows=1)    
    wls=data[:,0]
    trans=maximum(data[:,1],1)
    trans=data[:,1]
    ax2.plot(wls,trans,color=colors[k],linewidth=1.5,label = labs[k],alpha=0.8)
    
legend(loc=0)
ax2.set_ylim(0,200)
ax.set_xlim(0,80)

ax.set_xlabel(r"Wavelength ($\mu$m)",size=26)
text(0.03,0.05,"(a)",fontsize=22,transform=ax.transAxes) 
ax2.set_ylabel(r"Transmittance ($\%$)",size=26)
ax2.grid()
ax.xaxis.grid()
ax.yaxis.grid()
show()    

#fig1.savefig("/home/quentin/Papiers/Libois2015_FIRR/Figures/Filters.pdf",dpi=300,format="pdf")
#fig1.savefig("/home/quentin/Documents/Presentations/Figures/TOA_Filters.pdf",dpi=300,format="pdf")
#fig1.savefig("/home/quentin/Documents/Presentations/Figures/TOA.jpg",dpi=300,format="jpg")

