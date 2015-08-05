# -*- coding: utf-8 -*-

from FirrSeries import FirrSeries
from pylab import *
import matplotlib.dates as md

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

formatter = DateFormatter('%H:%M')

"""Analyze a series of FIRR sequences"""
filters_positions = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
filters = ['F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014']
list_filters = [filters_positions.index(f) for f in filters]
colors=["gold","red","blue","black","orange","yellow","cyan","green","Chartreuse","LightBlue"]

series = "Data/Series_2015-07-02"
data = FirrSeries(series)
date_series = data.date

print "Date of measurements:",date_series

npos=10

data.get_radiance(filters,npos,method="next",save=False)
time_series = data.time_series 

bt_series = data.bt_series
bt_series = ma.masked_equal(bt_series,0) 
radiance_series = data.radiance_series
radiance_series = ma.masked_equal(radiance_series,0)   
   
"""Figure"""
fig,(ax1,ax2) = subplots(1,2,figsize=(18,8))
fig.subplots_adjust(bottom=0.15)

for k in list_filters:
    ax1.plot(time_series[:],radiance_series[:,k],"o-",color=colors[k])
    ax2.plot(time_series[:],bt_series[:,k]-273.15,"o-",color=colors[k])
    
ax1.set_ylim(0,14)
ax1.grid()
ax1.set_xlabel("Time",size=20)
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=20)
plt.setp(ax1.xaxis.set_major_formatter(formatter))
ax1.set_ylabel("Radiance (W~m$^{-2}$~sr$^{-1}$)",size=20)

ax2.set_ylim(-80,30)
ax2.grid()
ax2.set_xlabel("Time (UTC)",size=20)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=20)
plt.setp(ax2.xaxis.set_major_formatter(formatter))
ax2.set_ylabel("Brightness temperature ($^{\circ}$C)",size=20)

show()
   
  