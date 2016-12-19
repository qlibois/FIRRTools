# -*- coding: utf-8 -*-

from pylab import *
from FirrRaw import FirrRaw

#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'17'})
rc('text', usetex=True)
##--------------------------------------
#
rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)

""" Read a sample raw file and return the correspondin mirror position, filter position, number of frames, \
number of pixels per frame, average frame and standard deviation of all frames"""

rawfile = "Data/test.raw"
#rawfile = "/home/quentin/FIRR/Eureka/TB_FIRR/FIRR_2016-02-27_21-19-12.0799_Data_000007.raw"

raw_data_nospav = FirrRaw(rawfile) # create a FirrRaw object
raw_data_spav = FirrRaw(rawfile) 

raw_data_nospav.analyze() # Analyze the file to extract all necessary information
raw_data_spav.analyze(spav="fast")

print "mean counts",raw_data_spav.mean

raw_data_spav.analyze(spav=2)

print "mean counts",raw_data_spav.mean


print "mirror position",raw_data_nospav.mpos
print "filter position",raw_data_nospav.fpos
print "number of frames",raw_data_nospav.nframes
print "number of pixels per frame",raw_data_nospav.npixels
print "number of bad pixels",raw_data_nospav.npixels-len(raw_data_nospav.correct_pixels)

mean_image_nospav = raw_data_nospav.mean
std_image_nospav = raw_data_nospav.std

mean_image_spav = raw_data_spav.mean
std_image_spav = raw_data_spav.std

"""Figure"""
fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(15,12))

fig.subplots_adjust(bottom=0.05,top=0.9,left=0.05,right=0.95,hspace=0.25,wspace=0.15)
image1 = ax1.imshow(mean_image_nospav.reshape(60,80),vmin=30000,vmax=40000)
colorbar(image1,ax=ax1,shrink=0.8)

image2 = ax2.imshow(std_image_nospav.reshape(60,80),vmin=0,vmax=2)  
colorbar(image2,ax=ax2,shrink=0.8)

image3 = ax3.imshow(mean_image_spav.reshape(60,80),vmin=30000,vmax=40000)  
colorbar(image3,ax=ax3,shrink=0.8)

image4 = ax4.imshow(std_image_spav.reshape(60,80),vmin=0,vmax=2)  
colorbar(image4,ax=ax4,shrink=0.8)

ax1.set_title("Mean Frame")
ax2.set_title("Standard deviation")
ax3.set_title("Mean Frame")
ax4.set_title("Standard deviation")

figtext(0.5,0.9,"No spatial average",horizontalalignment = 'center',size=20)
figtext(0.5,0.45,"Spatial average",horizontalalignment = 'center',size=20)

show()
           