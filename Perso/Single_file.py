# -*- coding: utf-8 -*-


"""Display the 2D image of detector counts and std for each of raw files in files"""
from pylab import *
from FirrSequence import FirrSequence
from FirrRaw import FirrRaw
#-------------Latex Style--------------
rc('font',**{'family':'serif','serif':['Computer Modern'],'size':'16'})
rc('text', usetex=True)
#--------------------------------------

rc('xtick',labelsize=22) 
rc('ytick',labelsize=22)
#--------------------------------------

labs=["open","10-12$\mu$m","12-14$\mu$m","17-18.5$\mu$m","22.5-27.5$\mu$m","7.9-9.5$\mu$m","20.5-22.5$\mu$m","18.5-20.5$\mu$m","17.25-19.75$\mu$m","30-50$\mu$m","blank"]


fichier = "/media/quentin/LACIE SHARE/FIRR_measurements/LR-TECH/SET2/2015-07-30_22-11-09.0834/Data_000004.raw" 
raw_file = FirrRaw(fichier)

f = open(fichier,'rb') # open raw file    
header = np.fromfile(f, dtype=np.uint32,count=4)
access_table = np.fromfile(f, dtype=np.uint16,count=raw_file.npixels) # id of the used pixels on the 120 x 160 standard grid of the bolometer     
tms = []
data_1D = []  # list to save all frames
data_1D_non_ill = []

illuminated = list(loadtxt("../Params/illuminated_pixels_193.txt"))
frame_number = 1000
data_1D = []
for k in range(min(frame_number,raw_file.nframes)):
    t = np.fromfile(f, dtype=np.uint32,count=1) # frame timestamp  
    frame = array(np.fromfile(f, dtype=np.uint16,count=raw_file.npixels)).astype(float) # values for all pixels, returned in a 1D array 

    if len(frame) == raw_file.npixels: # prevent from keeping erroneous frames             
        data_1D+=[frame[illuminated]] 

data_1D = array(data_1D) 
print shape(data_1D)       

data_1pixel = data_1D[:,20]-mean(data_1D[:,20]) 
data_193pixels = mean(data_1D,axis=1)-mean(mean(data_1D,axis=1))    

data_1frame = data_1D[0,:]-mean(data_1D[:50],axis=0)
data_200frames = mean(data_1D,axis=0)-mean(data_1D[:50,:],axis=0)

fig=figure(13,figsize=(8,6))
plot(data_1pixel,color="blue",linewidth=1.5,label="1 pixel")
plot(data_193pixels,color="red",linewidth=1.5,label="193 pixels")
ylabel("Counts",size=22)
xlabel("Frame number",size=22)
ylim(-5,5)
legend(loc=0)      

fig.savefig("/home/quentin/Documents/Presentations/Figures/Noise1.jpg",dpi=300,format="jpg")

fig=figure(14,figsize=(8,6))
plot(data_1frame,color="blue",linewidth=1.5,label="1 frame")
plot(data_200frames,color="red",linewidth=1.5,label="200 frames")
ylabel("Counts",size=22)
xlabel("Pixel number",size=22)
ylim(-5,5)
legend(loc=0)     

fig.savefig("/home/quentin/Documents/Presentations/Figures/Noise2.jpg",dpi=300,format="jpg")

std0 = []
nf = [1,2,3,4,5,10,20,50,75,100,150,200]
for k in nf:
    std0+=[std(mean(data_1D[:k,:],axis=0)-mean(data_1D[:1],axis=0))]
    
fig=figure(15,figsize=(8,6))    
plot(nf,std0)
show()
