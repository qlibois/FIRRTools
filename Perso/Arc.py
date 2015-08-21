# -*- coding: utf-8 -*-
"""
Created on Thu Feb 05 16:45:01 2015

@author: User0000
"""

from pylab import *
from datetime import datetime

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]

tir = 'F0009'
fir = 'F0014'

date="2015-02-21"
bt_file = "QuickLookData/Brightness_Temperature_%s.txt"%date

def plot_arc(name_file,b1,b2,s,e):
    dates = []
    bt = []
    fichier = open(name_file,"r")
    for line in fichier:
        if line.startswith("2015"):
            data=line.split()
            dates+=[datetime.strptime(data[0], "%Y-%m-%d_%H-%M-%S")]
            bt+=[array([float(x.replace("--","0")) for x in data[1:]])]
    
    a,b = searchsorted(dates,[s,e])        
    bt=array(bt)    
    plot(bt[a:b,b2]-273.15,bt[a:b,b2]-bt[a:b,b1],"o-",label="%s"%date)

ntir = all_filters.index(tir)
nfir = all_filters.index(fir)

s = datetime(2015,02,21,12,51)
e = datetime(2015,02,21,12,53)

plot_arc(bt_file,ntir,nfir,s,e) 

#fichier="cloudy_sky_2015_02_22.txt"
#plot_arc(fichier,4,9)    
#fichier="cloudy_sky_2015_02_23.txt"
#plot_arc(fichier,4,9)   

#xlim(200,260)
#ylim(0,60)
    
legend(loc=0)    
show()        