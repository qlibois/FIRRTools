# -*- coding: utf-8 -*-

import glob
import os
from pylab import *
from datetime import datetime
from FirrSequence import FirrSequence
from FirrSeries import FirrSeries
from matplotlib import rc
from matplotlib import dates
import Toolbox
import csv
from matplotlib.dates import date2num
from scipy import stats

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

ordered_filters = ['F0007','F0008','F0009','F0034','F0035','F0010','F0036','F0011','F0014']
all_filters = ['open','F0008','F0009','F0034','F0011','F0007','F0036','F0035','F0010','F0014','blank','open','open','open','open','open','open']
list_filters=[0,1,2,3,4,5,6,7,8,9,10]
labs=["open","10-12~$\mu$m","12-14~$\mu$m","17-18.5~$\mu$m","22.5-27.5~$\mu$m","7.9-9.5~$\mu$m","20.5-22.5~$\mu$m","18.5-20.5~$\mu$m","17.25-19.75~$\mu$m","30-50~$\mu$m","blank"]
wls=array([0,11,13,17.75,25,8.7,21.5,19.5,18.5,40,0])
colors=["grey","DarkOrange","Red","Chartreuse","cyan","Gold","LightBlue","green","black","blue"]
illuminated = list(loadtxt("../Params/illuminated_pixels.txt")) # illuminated pixels

meas = "SET2"

""" Temperature of the Nadir BB """

if meas == "SET1":   # less temperatures
    csvfile = open('/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/20150730_Run_CSV/20150730_26C.csv','rb')

elif meas == "SET2": # all temperatures
    csvfile = open('/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/20150731_SET2_CSV/20150730_210108.csv','rb')

fichier_temp = csv.reader(csvfile)
rad_nadir = []
dates = [] 
t_nadir = []
t_zenith = []

for line in fichier_temp:
    if line[0].startswith("Jul"):
        day=line[0][4:6]
        hour = line[1]
        date = datetime(2015,07,int(day),int(hour[:2]),int(hour[3:5]),int(hour[6:8]))       
        dates+=[date]           
        t_nadir+=[0.8*float(line[5])+0.1*(float(line[3])+float(line[4]))]
        t_zenith+=[0.8*float(line[8])+0.1*(float(line[6])+float(line[7]))]
#        t_nadir+=[0.8*float(line[8])+0.1*(float(line[6])+float(line[7]))] # zenith actually
        
        
# Select only files with sufficiently stable temperature (over one minute)       
t_nadir = array(t_nadir)
t_zenith = array(t_zenith)

l = len(dates)
span = 60
sigma_nadir = zeros_like(t_nadir)
selection = zeros_like(t_nadir)
for k in range(span/2,l-span/2):
    sigma_nadir[k] =  std(t_nadir[k-span/2:k+span/2])
    if sigma_nadir[k]<0.0025:
        selection[k] = 1

#plot(dates,t_zenith,"r-")
#plot(dates,t_nadir,"k-")
#show()             

em = loadtxt("../Params/emissivity.dat") # BB emissivity
emiss_wls = em[:,0]
emiss = em[:,1] 


"""-----------Extract some NBB measurements only--------------"""
print "Computing NBB radiances"
dates_select = []
rad_nadir = []   
new_select = []     
count = 0
for k in range(0,l,120):  
    if selection[k] == 1:
        dates_select+=[dates[k]]            
        rad_nadir+=[Toolbox.radiance_BB(t_nadir[k]+273.15,fil,emiss_wls,emiss,24+273.15) for fil in all_filters]

n_select = len(dates_select)  
rad_nadir = reshape(array(rad_nadir),(n_select,17))
dnum = array([date2num(dates[k]) for k in range(l)])

print "NBB radiances Computed"

"""-------------FIRR measurements--------"""
if meas == "SET1":
    series = FirrSeries("/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1")
elif meas == "SET2":    
    series = FirrSeries("/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2")
    
# Extract FIRR temperatures (BB + pointing mirror)    
sequences = series.sequences
series.get_temperature()
temp_firr = series.temperature
temp_firr_time = series.temp_time   

firr_hbb = temp_firr[:,0]
firr_abb = temp_firr[:,1]
firr_pm = temp_firr[:,7]

rad = []
tms = []

nf = len(sequences)
print nf
#nf = 30

counts_nadir = ma.zeros([11,nf])
counts_hbb = ma.zeros([11,nf])
counts_abb = ma.zeros([11,nf])
counts_zbb = ma.zeros([11,nf])
rad_nad = zeros([11,nf])
rad_hbb = zeros([11,nf])
rad_abb = zeros([11,nf])
rad_zbb = zeros([11,nf])
rad_firr = ma.zeros([11,nf])
dates_firr=[]

mean_counts = []
mean_rad = []
std_counts = []
temp_counts = []
temp_rad = []
last_rad = zeros([11])
last_ind = 0
start = 0
nvalues = []
t_nad = []
valid_temp = [] # different NBB temperatures
temp_error = []
mean_error = []
std_error = []

for k,s in enumerate(sequences[:nf]):   # sequence AHNZ_no_open  
#for k,s in enumerate(sequences[49:52]):
    print k,s
    seq = FirrSequence(s,10,s, detector = 3, illuminated_pixels = 69)
    tms0 = seq.date0
    ind = searchsorted(dates,tms0)
    ind_firr = searchsorted(temp_firr_time,tms0)
    print "%s/%s %s"%(k,nf,tms0)
    dates_firr+= [tms0]
    t_nad+= [t_nadir[ind]]
    
    if selection[ind] == 1: #  in NBB stable conditions
        print "-----------------------New data---------------------"
        # 1-Calculate theoretical radiances        
        rad_nad[:,k] = array([Toolbox.radiance_BB(t_nadir[ind]+273.15,all_filters[j],emiss_wls,emiss,firr_pm[ind_firr]+273.15) for j in list_filters])
        rad_hbb[:,k] = array([Toolbox.radiance_BB(firr_hbb[ind_firr]+273.15,all_filters[j],emiss_wls,emiss,firr_pm[ind_firr]+273.15) for j in list_filters])
        rad_abb[:,k] = array([Toolbox.radiance_BB(firr_abb[ind_firr]+273.15,all_filters[j],emiss_wls,emiss,firr_pm[ind_firr]+273.15) for j in list_filters])        
        rad_zbb[:,k] = array([Toolbox.radiance_BB(t_zenith[ind]+273.15,all_filters[j],emiss_wls,emiss,firr_pm[ind_firr]+273.15) for j in list_filters])
   
        diff = abs(rad_nad[:,k]-last_rad) # detect new temperature step               
        if start == 1 and any(diff > 0.05):             
            nvalues+=[shape(temp_counts)[0]] # number of sequences at each temperature step
            valid_temp+=[previous_temp]
            print "-----------------------New temperature--------------",previous_temp
            temp_counts = ma.masked_array(temp_counts)
            temp_rad = ma.masked_array(temp_rad) 
            mean_counts+=[mean(temp_counts,axis=0)]
            std_counts+=[std(temp_counts,axis=0)]
            mean_rad+=[mean(temp_rad,axis=0)]  
            temp_error = ma.masked_array(temp_error)
            mean_error+=[mean(temp_error,axis=0)]  
            std_error+=[std(temp_error,axis=0)]                
            temp_counts = []
            temp_rad = []
            temp_error = []
            
        previous_temp = t_nadir[ind]    
        start = 1    
        last_rad = rad_nad[:,k]             
        seq.get_radiance(all_filters[:10],method="None",spav="fast",non_ill=1)
        rad_firr[:,k] = seq.all_radiance[:11,0] # SET 2 Nadir
        temp_error+=[rad_firr[:,k]-rad_nad[:,k]] 

#        rad_firr[:,k] = seq.all_radiance[:11,1] # SET 1 Zenith
#        temp_error+=[rad_firr[:,k]-rad_zbb[:,k]] 
        counts_nadir[:,k] = ma.average(seq.all_mean[:11,2,:],axis=1)-ma.average(seq.all_mean[:11,1,:],axis=1)
#        counts_nadir[:,k] = ma.average(seq.all_mean[:11,2,:],axis=1)-ma.average(seq.all_mean[:11,0,:],axis=1) # only two pixels because spatial average 
        # using ABB because probably more stable
#        counts_nadir[:,k] = mean(seq.all_mean[:,2,illuminated],axis=1)-mean(seq.all_mean[:,0,illuminated],axis=1) # using ABB because probably more stable
        
        counts_hbb[:,k] = mean(seq.all_mean[:11,1,:],axis=1)-mean(seq.all_mean[:11,1,:],axis=1) 
        counts_abb[:,k] = mean(seq.all_mean[:11,0,:],axis=1)-mean(seq.all_mean[:11,1,:],axis=1) 
        counts_zbb[:,k] = mean(seq.all_mean[:11,3,:],axis=1)-mean(seq.all_mean[:11,1,:],axis=1)
        temp_counts+=[counts_nadir[:,k]]
        print "counts_nadir",k,seq.all_mean[:11,2,0]
        temp_rad+=[rad_nad[:,k]]

# Last step
print "New temperature"
nvalues+=[shape(temp_counts)[0]] # number of sequences at each temperature step
valid_temp+=[previous_temp]
temp_counts = ma.masked_array(temp_counts) # eliminates bad values
temp_rad = ma.masked_array(temp_rad)            
mean_counts+=[mean(temp_counts,axis=0)]
std_counts+=[std(temp_counts,axis=0)]
mean_rad+=[mean(temp_rad,axis=0)]  
temp_error = ma.masked_array(temp_error)
mean_error+=[mean(temp_error,axis=0)]  
std_error+=[std(temp_error,axis=0)] 
valid_temp = array(valid_temp)

print "valid_temp",valid_temp 

#for j in range(11):
#    plot(dates_firr,counts_nadir[j,:3],"o-")
#    plot(dates_firr,counts_abb[j,:3],"o--")
#show()
#
#plot(t_nad,counts_nadir[1,:],"o-")
#show()

mean_rad = array(mean_rad)
mean_counts = array(mean_counts)
std_counts = array(std_counts) 
mean_error = array(mean_error)
std_error = array(std_error) 

print shape(mean_rad),shape(mean_counts),shape(std_counts)

print "number of measurements used",nvalues
x = linspace(0,30)

fig = figure(5,figsize=(13,8))

npoints,nfil = shape(mean_rad)
details = zeros([nfil,3]) # mean std_counts, slope, std_error

for fil in ordered_filters:
    j = all_filters.index(fil)       
    slope, intercept, r_value, p_value, std_err = stats.linregress(mean_rad[:,j],mean_counts[:,j])  
    plot(x,x*slope+intercept,color=colors[j],label="%s -- %.2f"%(labs[j],slope),alpha=0.5)
    grid()
#    plot(rad_abb[j,:],counts_abb[j,:],"o",color="k")
#    plot(rad_hbb[j,:],counts_hbb[j,:],"o",color="k")
#    plot(rad_zbb[j,:],counts_zbb[j,:],"o",color="k")
    errorbar(mean_rad[:,j],mean_counts[:,j],yerr=std_counts[:,j],xerr=0,marker="o",linestyle="",markersize=3,mew=1.,mfc=colors[j],mec="k",elinewidth=1.5,color=colors[j])
    details[j,0] = mean(std_counts[:,j])
    details[j,1] = slope
    details[j,2] = std_err    
        
legend(loc=0)    
xlabel(r"Radiance (W~m$^{-2}$~sr$^{-1}$)",size=24)
ylabel(r"Counts difference",size=24)    
#ylim(-300,300)
ylim(-50,600)

show()

#fig.savefig("/home/quentin/Papiers/Libois2015_FIRR/Figures/LRTech_Linearity.pdf",dpi=300,format="pdf")     
#fig.savefig("/home/quentin/Documents/Presentations/Figures/LRTech_Linearity.jpg",dpi=300,format="jpg")  

x = linspace(-50,70)
fig1 = figure(1,figsize=(13,8))

print "mean_error",mean_error
print "std_error",std_error

savetxt("temperature_steps.dat",valid_temp) 
savetxt("mean_counts.dat",mean_counts) 
savetxt("std_counts.dat",std_counts) 
savetxt("mean_error.dat",mean_error) 
savetxt("std_error.dat",mean_error) 
savetxt("details.dat",details) 
savetxt("number_of_sequences.dat",array(nvalues))

for num,fil in enumerate(ordered_filters):
    j = all_filters.index(fil)  
    plot([0,1],[-10,-10],color=colors[j],label=labs[j],alpha=0.5)
    print "mean_error[:,j]",mean_error[:,j]
    errorbar(valid_temp+(num-5)*0.4,mean_error[:,j],yerr=std_error[:,j],xerr=0,marker="o",linestyle="",markersize=3,mew=1.,mfc=colors[j],mec="k",elinewidth=1.5,color=colors[j])
#    plot(t_nad,rad_firr[j,:]-rad_nad[j,:],"o",markersize=3,color=colors[j])
    plot(x,0*x,"k")
#    figure(2)
#    plot(dates_firr,rad_firr[j,:],"o",color=colors[j])
#    plot(dates_firr,rad_nad[j,:],"-",color=colors[j])
 
figure(1) 
ax=gca()
legend(loc=0)
xlim(-30,60)
grid()
ylim(-0.15,0.25)
ylabel(r"Radiance difference (W~m$^{-2}$~sr$^{-1}$)",size=24)
xlabel(r"Temperature ($^{\circ}$C)",size=24)
text(0.04,0.05,"(a)",fontsize=22,transform=ax.transAxes) 

#fig1.savefig("/home/quentin/Papiers/Libois2015_FIRR/Figures/LRTech_ZBB_Retrieval.pdf",dpi=300,format="pdf")

show()

fig1.savefig("/home/quentin/Papiers/Libois2015_FIRR/Figures/LRTech_NBB_Retrieval.pdf",dpi=300,format="pdf")

