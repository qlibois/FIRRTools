# -*- coding: utf-8 -*-

from FirrSeries import FirrSeries
from pylab import *
from datetime import datetime

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

formatter = DateFormatter('%H:%M')

"""Analyze a series of FIRR sequences"""
filters_positions = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
filters_positions = ['F0011','F0007','F0036','F0035','F0010','F0014','F0008','F0009','F0034','open','open','blank','open','open','blank','open','open']

filters = ['F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014']
list_filters = [filters_positions.index(f) for f in filters]
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]
labs=["open","10-12$\mu$m","12-14$\mu$m","17-18.5$\mu$m","22.5-27.5$\mu$m","7.9-9.5$\mu$m","20.5-22.5$\mu$m","18.5-20.5$\mu$m","17.25-19.75$\mu$m","30-50$\mu$m","blank"]


#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-06-UQAM/2015-07-02"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-02-INO/2015-02-20/Sky"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-02-INO/2015-02-21/Sky"
series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-11"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-13"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-20/2015-04-20-2"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-21"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-13/Snow_Calib/"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-14"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-05"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-12"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-09"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-10"
#series = "/media/quentin/LACIE SHARE/FIRR_measurements/Eureka/2015-10-24"
series = "/media/quentin/LACIE SHARE/FIRR_measurements/Eureka/2016-02-24"

#start_meas=datetime(2016,3,16,10)
#end_meas=datetime(2016,3,16,12)

start_meas=datetime(2014,10,29,0)
end_meas=datetime(2016,10,30,18)

#start_meas=datetime(2015,10,24,10)
#end_meas=datetime(2015,10,24,11)
#
#start_meas=datetime(2015,4,8,14,38)
#end_meas=datetime(2015,4,8,16,27)

#start_meas=datetime(2015,4,9,20,50)
#end_meas=datetime(2015,4,9,21,20)

#start_meas=datetime(2015,4,10,1)
#end_meas=datetime(2015,4,10,22,23)
#
#start_meas=datetime(2015,4,11,14,40)
#end_meas=datetime(2015,4,11,16,10)
#
#start_meas=datetime(2015,4,12,19)
#end_meas=datetime(2015,4,12,20)
#
#start_meas=datetime(2015,4,12,1)
#end_meas=datetime(2015,4,12,20)

#start_meas=datetime(2015,4,21,16)
#end_meas=datetime(2015,4,21,17)
#
#start_meas=datetime(2015,4,7,18,50)
#end_meas=datetime(2015,4,7,20)

#start_meas=datetime(2015,4,20,22,30)
#end_meas=datetime(2015,4,20,23,30)

#start_meas=datetime(2015,4,5,9,50)
#end_meas=datetime(2015,4,5,10,43)
#
#start_meas=datetime(2015,4,11,19,55)
#end_meas=datetime(2015,4,11,20,55)
##
#start_meas=datetime(2015,4,11,17,23)
#end_meas=datetime(2015,4,11,18,15)
#
#start_meas=datetime(2015,4,13,18)
#end_meas=datetime(2015,4,13,19,15)
#
#start_meas=datetime(2015,4,13,19,50)
#end_meas=datetime(2015,4,13,20,50)
#
#start_meas=datetime(2015,4,14,1)
#end_meas=datetime(2015,4,14,23)

data = FirrSeries(series,start_meas,end_meas,detector=3,illuminated_pixels=145)
date_series = data.date

npos=11
data.get_radiance(filters,npos,method="next",spav="fast",non_ill=1,save=True,name_output = "2016-02-24")

time_series = data.time_series 

bt_series = data.bt_series
bt_series = ma.masked_equal(bt_series,0) 
G_series = data.gain_series

G_series = ma.masked_equal(G_series,0)
radiance_series = data.radiance_series
radiance_series = ma.masked_equal(radiance_series,0)  
   
"""Figure"""
fig,(ax1,ax2) = subplots(1,2,figsize=(18,8))
fig.subplots_adjust(bottom=0.15)

for k in list_filters:
#    figure(8)
#    plot(time_series[::3],G_series[:,k])
#    show()
    ax1.plot(time_series[:],radiance_series[:,k],"o-",color=colors[k],label = labs[k])
    ax2.plot(time_series[:],bt_series[:,k]-273.15,"o-",color=colors[k])
#show()   
ax1.set_ylim(0,8)
ax1.grid()
ax1.set_xlabel("Time",size=20)
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=20)
plt.setp(ax1.xaxis.set_major_formatter(formatter))
ax1.set_ylabel("Radiance (W~m$^{-2}$~sr$^{-1}$)",size=20)

ax2.set_ylim(-40,-20)
ax2.grid()
ax2.set_xlabel("Time (UTC)",size=20)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=20)
plt.setp(ax2.xaxis.set_major_formatter(formatter))
ax2.set_ylabel("Brightness temperature ($^{\circ}$C)",size=20)


ax1.legend(loc=0)
show()
   
  