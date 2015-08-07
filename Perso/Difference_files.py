# -*- coding: utf-8 -*-


"""Display the 2D image of detector counts and std for each of raw files in files"""
from pylab import *
from FirrSequence import FirrSequence

labs=["open","10-12$\mu$m","12-14$\mu$m","17-18.5$\mu$m","22.5-27.5$\mu$m","7.9-9.5$\mu$m","20.5-22.5$\mu$m","18.5-20.5$\mu$m","17.25-19.75$\mu$m","30-50$\mu$m","blank"]


directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/2015-07-30_13-26-44.0834" # 26°C
directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/2015-07-30_16-29-09.0957" # 35°C
#directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET1/2015-07-30_19-01-57.0327" # 55°C
#directory = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_21-11-28.0353" # 55°C

sequence = FirrSequence(directory,10,directory)
sequence.organized(spav="None")

counts = sequence.all_mean

ambient = counts[:,0,:]
hot = counts[:,1,:]
nadir = counts[:,2,:]
zenith = counts[:,3,:]

for j in range(11):
#    imshow(reshape(hot[j,:]-zenith[j,:],(60,80)),vmin=-2,vmax=2)
    imshow(reshape(zenith[j,:]-nadir[j,:],(60,80)),vmin=-1,vmax=1)
    colorbar()
    title("%s"%labs[j])
    show()
    