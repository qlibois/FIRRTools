# -*- coding: utf-8 -*-


"""Display the 2D image of detector counts and std for each of raw files in files"""
from pylab import *
from FirrSequence import FirrSequence

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'14'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
#--------------------------------------

labs=["open","10-12$\mu$m","12-14$\mu$m","17-18.5$\mu$m","22.5-27.5$\mu$m","7.9-9.5$\mu$m","20.5-22.5$\mu$m","18.5-20.5$\mu$m","17.25-19.75$\mu$m","30-50$\mu$m","blank"]


directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/2015-07-30_13-26-44.0834" # 26°C
directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/2015-07-30_16-29-09.0957" # 35°C
#directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/2015-07-30_19-01-57.0327" # 55°C
#directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_21-11-28.0353" # 55°C
directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-31_00-22-52.0748"
directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-31_00-16-56.0710"

directory = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-11/2015-04-11_20-13-48.0645"

directory = "/media/quentin/LACIE SHARE/FIRR_measurements/2015-04-NETCARE/2015-04-11/2015-04-11_20-39-02.0032"
#
sequence = FirrSequence(directory,10,directory)
sequence.organized(spav="None")

counts = sequence.all_mean
stds = sequence.all_std

std_nad = stds[:,2,:]

#savetxt("background_ref.txt",counts[3,0,:])

ambient = counts[:,0,:]
hot = counts[:,1,:]

for j in range(1,12):
    for nv in range(3):
        fig = figure(12)
        diff = reshape(counts[j,2+nv,:]-ambient[j,:],(60,80))
        vmax = amax(diff)
        imshow(diff,interpolation="None",vmax = vmax,vmin=vmax*0.9)
        title(labs[j])
        colorbar(shrink=0.8)
        show()
    
    