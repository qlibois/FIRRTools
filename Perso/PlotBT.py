# -*- coding: utf-8 -*-

from pylab import *
from datetime import datetime
from matplotlib import rc
from matplotlib import dates

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

"""Plot brightness temperature from a file in QuickLookData"""
filtres=['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
list_filters=[1,2,3,4,5,6,7,8,9]
labs=["open","10-12$\mu$m","12-14$\mu$m","17-18.5$\mu$m","22.5-27.5$\mu$m","7.9-9.5$\mu$m","20.5-22.5$\mu$m","18.5-20.5$\mu$m","17.25-19.75$\mu$m","30-50$\mu$m","blank"]

#date="2015-02-21"
date="2015-07-02"
#date="2015-02-21"

colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]

time=[]
bt=[]

f=open("QuickLookData/Brightness_Temperature_%s.txt"%date,"r")
for line in f:  
    if line.startswith("2015"):
        time+=[datetime.strptime(line.split()[0],"%Y-%m-%d_%H-%M-%S")]
        bt+=[array([float(x.replace("--","0")) for x in line.split()[1:]])]

bt=array(bt)

print bt
bt=ma.masked_equal(bt,0)

fig=figure(12,figsize=(15,8))  
fig.subplots_adjust(left=0.1,right=0.94,top=0.97)

hfmt = dates.DateFormatter('%H:%M')
ax=gca()
ax.xaxis.set_major_formatter(hfmt)

#plot(time[2:-1],bt[2:-1,4]-bt[2:-1,2],"o-")
#show()
#     

for k in list_filters:
    plot(time[2:-1],bt[2:-1,k]-273.15,"o-",markersize=2,mew=1.5,mfc="white",mec=colors[k],linewidth=1,label=filtres[k],color=colors[k])
       
#xlabel(r"Black Body Radiance (W m$^{-2}$ sr$^{-1}$)",size=20)
ylabel(r"Brightness temperature ($^{\circ}$C)",size=22)
legend(loc=4,numpoints=1)  
#ax.set_yticks(range(-10,60,5))
ylim(-90,0)
grid() 
 
show()  

#fig.savefig("/home/quentin/PostDoc/Ecrit/Figures/brightness_temperature_%s.pdf"%date,dpi=300,format="pdf")  
     