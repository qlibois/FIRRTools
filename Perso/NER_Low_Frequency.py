# -*- coding: utf-8 -*-

from FirrSequence import FirrSequence
from FirrSeries import FirrSeries
from pylab import *
import matplotlib.dates as md

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
#--------------------------------------

formatter = DateFormatter('%H:%M')

ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0010','F0036','F0011','F0014']
all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank']
labs=["open","10-12~$\mu$m","12-14~$\mu$m","17-18.5~$\mu$m","22.5-27.5~$\mu$m","7.9-9.5~$\mu$m","20.5-22.5~$\mu$m","18.5-20.5~$\mu$m","17.25-19.75~$\mu$m","30-50~$\mu$m","blank"]
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue","pink"]

series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-02-INO/2015-02-22/ZBB_Retrieval/"
series = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-02-INO/2015-02-22/Sky"
series = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2"
data = FirrSeries(series)
date_series = data.date

#data.get_temperature()
#plot(data.temp_time,data.temperature[:,[0,1]])
#show()

npos = 10

print "Date of measurements:",date_series

abb = []
hbb = []
abb_non_ill = []
hbb_non_ill = []
time = []
diff = []
diff_non_ill = []

for seq in data.sequences[80:120]:
    print seq
    seq=FirrSequence(seq,npos,seq)
    time+=[seq.date0]
    seq.organized(spav="fast",non_ill=0)  
    abb+=[seq.all_mean[:,0,0]]
    hbb+=[seq.all_mean[:,1,0]]
    diff+=[seq.all_mean[:,0,0]-seq.all_mean[:,1,0]]
    seq.organized(spav="fast",non_ill=1)    
    abb_non_ill+=[seq.all_mean[:,0,0]]
    hbb_non_ill+=[seq.all_mean[:,1,0]]
    diff_non_ill+=[seq.all_mean[:,0,0]-seq.all_mean[:,1,0]]

abb = array(abb)
hbb = array(hbb) 
abb_non_ill = array(abb_non_ill)
hbb_non_ill = array(hbb_non_ill) 
diff = array(diff)
diff_non_ill = array(diff_non_ill) 

fig = figure(12,figsize=(12,6))            
for fil in ["F0008"]:#ordered_filters:
    k = all_filters.index(fil)
    plot(time,diff[:,k]-mean(diff[:,k]),"b",marker="o",linestyle="-",linewidth=1.5,markersize=4,mew=1.,mfc="w",mec="k",color="k",label=r"Non corrected data")
    plot(time,diff_non_ill[:,k]-mean(diff_non_ill[:,k]),"b",marker="o",linestyle="-",linewidth=1.5,markersize=4,mew=1.,mfc="w",mec="r",color="r",label=r"Corrected data")
    print(std(diff[:,k]))
    print(std(diff_non_ill[:,k])) 
   
grid()   
gca().xaxis.set_major_formatter(formatter)
#gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))   
xlabel(r"Time",size=20)
ylabel(r"Normalized counts",size=20)
legend(loc=0,numpoints=1)
show()
             

fig.savefig("/home/quentin/Papiers/FIRR_AMT/Figures/NER_LF.pdf",dpi=300,format="pdf")
