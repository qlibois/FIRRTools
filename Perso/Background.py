# -*- coding: utf-8 -*-

from FirrSeries import FirrSeries
from FirrSequence import FirrSequence
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

series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-02-INO/2015-02-22/ZBB_Retrieval/"
series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-02-INO/2015-02-22/Sky"
data = FirrSeries(series)
date_series = data.date

data.get_temperature()

plot(data.temp_time,data.temperature)
show()

npos = 11

print "Date of measurements:",date_series

abb = []
hbb = []
abb_non_ill = []
hbb_non_ill = []
time = []

for seq in data.sequences[40:]:
    print seq
    seq=FirrSequence(seq,npos,seq)
    time+=[seq.date0]
    seq.organized(spav="fast",non_ill=0)    
    abb+=[seq.all_mean[2,0,0]]
    hbb+=[seq.all_mean[2,1,0]]
    seq.organized(spav="fast",non_ill=1)    
    abb_non_ill+=[seq.all_mean[1,0,0]]
    hbb_non_ill+=[seq.all_mean[1,1,0]]

abb = array(abb)
hbb = array(hbb) 
abb_non_ill = array(abb_non_ill)
hbb_non_ill = array(hbb_non_ill) 
#plot(time,hbb-abb-mean(hbb-abb),"b",label="No correction")  
#plot(time,hbb_non_ill-abb_non_ill-mean(hbb_non_ill-abb_non_ill),"r",label="Non-illuminated correction") 
plot(time,hbb-mean(hbb),"b",label="HBB No correction")  
#plot(time,hbb_non_ill-mean(hbb_non_ill),"r",label="HBB Non-illuminated correction") 
plot(time,abb-mean(abb),"r",label="ABB No correction") 
#title("HBB, %s"%filters_positions[1],size=20)  
xlabel("Time",size=20)
ylabel("Counts",size=20)
legend(loc=0)
show()
