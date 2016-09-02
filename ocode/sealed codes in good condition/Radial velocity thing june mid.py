################## This is the code for radial velocity measurements #################
###### This does not include phase folding. I need to incorporate that into this script later######

import numpy as np
import matplotlib.pyplot as plt
import emcee
import ajplanet as ap
import corner
import scipy.constants as constnt
import astropy.constants as cst
import math

######################################################################################
####### I need to fit the respective gamma values for each data set together and then fit them ####

data1 = np.genfromtxt('radial velocity data set from paper.txt')
l1 = len(data1)

data2 = np.genfromtxt('radial velocity data set 2.txt')
l2 = len(data2)

#data2 = np.genfromtxt('combined RV data.txt')
#l2 = len(data2)

t1 = []  # for data 1
f1 = []
ferr1 = []

t2 = [] # for data 2
f2 = []
ferr2 = []

t3 = [] # for combined data
f3 = []
ferr3 = [] 

for x in range(0, l1): #to get the data in separate arrays
    t1.append(data1[x][0])
    f1.append(data1[x][1])
    ferr1.append(data1[x][2])
    
for x in range(0, l2): #to get the data in separate arrays
    t2.append(data2[x][0])
    f2.append(data2[x][1])
    ferr2.append(data2[x][2])

t3 = t1 + t2
f3 = f1 + f2
ferr3 = ferr1 + ferr2

t1 = np.array(t1)
f1 = np.array(f1)
ferr1 = np.array(ferr1)

f2levelled = f2

t2 = np.array(t2)
f2 = np.array(f2)
ferr2 = np.array(ferr2)

t3 = np.array(t3)
f3 = np.array(f3)
ferr3 = np.array(ferr3)

#%%
################################ Emcee iteration initialization########################

def lnlikerv(theta_free, theta_fixed, trv1, trv2, totalf, totalferror): ##give time for 1st, time for 2nd and the total flux and total fluxerror
    gamma1, gamma2, k1, k2, ecc1, ecc2, w1, w2 = theta_free
    t01,p1,t02,p2  = theta_fixed      
      
    modeldat11 = ap.pl_rv_array(trv1, 0 , k1, w1, ecc1, t01, p1) #data 1 for planet 1
    modeldat12 = ap.pl_rv_array(trv1, 0, k2, w2, ecc2, t02, p2) #data 1 for planet 2
    t_modeldat1 = modeldat11 + modeldat12 + gamma1
    
    modeldat21 = ap.pl_rv_array(trv2, 0 , k1, w1, ecc1, t01, p1)
    modeldat22 = ap.pl_rv_array(trv2, 0, k2, w2, ecc2, t02, p2)
    t_modeldat2 = modeldat21 + modeldat22 + gamma2
    
    t_model = np.concatenate((t_modeldat1,t_modeldat2))
    
    ffunc = 1
    inv_sigma = 1.0/((ffunc*totalferror)**2) #+ y_model**2*np.exp(2*lnf))
    return -0.5*(np.sum((totalf-t_model)**2*inv_sigma)) #- np.log(inv_sigma)))
    
def lnpriorrv(theta_free):
    gamma1,gamma2,k1,k2,ecc1,ecc2,w1,w2 = theta_free
    if  0 < w1 < 2*np.pi and 0 < w2 < 2*np.pi and 4 < gamma1 < 9 and 4 < gamma2 < 10 and 0 <= ecc1 < 1 and 0 <= ecc2 < 1 and 0 < k1 < 3 and 0 < k2 < 3:
        return 0.0            
    return -np.inf   

def lnprobrv(theta_free, theta_fixed, trv1, trv2, totalf, totalferror):
    lp = lnpriorrv(theta_free)
    if not np.isfinite(lp):
        return -np.inf
    ll = lnlikerv(theta_free, theta_fixed, trv1, trv2, totalf, totalferror)
    return lp + ll       
    
############################# The parameters values ###################################
##### These are the fixed values####
## the t0 values tat i have taken are of the first maximum assuming they both overlap there
    
t01 = 56813.3838955076789716 #### this and (taken from text file given by olivier)
p1 = 7.919 #orbital period 
i1 = 1.55336415 # obtained from iterationsof the script
        
t02 = 56817.2730369411219726  ### this needs to be changed when i switch the data set given
p2 = 11.90727 #orbital period
i2 = 88.92*np.pi/180  #orbital inclination obtained from the paper

###### the varying parameters ######

gamma1 = 7.20
gamma2 = 7.32
K1 = 0.05
K2 = 0.04
ecc1 = 0.119#0.119 #orbital eccentricity
ecc2 = 0.095#0.119 #orbital eccentricity
w1 = 179*np.pi/180 #argument of periastron 
w2 = 237*np.pi/180 #argument of periastron 
#ffunc = 1

########################### Calling emcee iteration ###################################

initial = [gamma1,gamma2,K1,K2,ecc1,ecc2,w1,w2]  ## the gamma and K values are dependent on the sinusoidal functions and not the data set considered
fixed = [ t01,p1,t02,p2]
ndim = len(initial)
nwalkers = 100

#Doing for the first data set ######
initial0 = [initial + 1e-2*np.random.randn(ndim) for i in range(nwalkers)] 

sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprobrv, args=(fixed,t1,t2,f3,ferr3))    #here we makes respective changes for the other data set by changing to t2, f2 and ferr2 

print("Running burn-in...")
number_of_iterations = 10000
sampler.run_mcmc(initial0, number_of_iterations)

samples = sampler.chain[:, 140:, :].reshape((-1, ndim)) ## to get all the parameter iterations

################ Printing all the walkers together ##################

plt.figure()
fig, axes = plt.subplots(8, 1, sharex=True, figsize=(8, 9))
axes[0].plot(sampler.chain[:, :, 0].T, color="k", alpha=0.4)
axes[0].set_ylabel("$gamma1$")

axes[1].plot(sampler.chain[:, :, 1].T, color="k", alpha=0.4)
axes[1].set_ylabel("$gamma2$")

axes[2].plot(sampler.chain[:, :, 2].T, color="k", alpha=0.4)
axes[2].set_ylabel("$K1$")

axes[3].plot(sampler.chain[:, :, 3].T, color="k", alpha=0.4)
axes[3].set_ylabel("$K2$")

axes[4].plot(sampler.chain[:, :, 4].T, color="k", alpha=0.4)
axes[4].set_ylabel("$ecc1$")

axes[5].plot(sampler.chain[:, :, 5].T, color="k", alpha=0.4)
axes[5].set_ylabel("$ecc2$")

axes[6].plot(sampler.chain[:, :, 6].T, color="k", alpha=0.4)
axes[6].set_ylabel("$w1$")

axes[7].plot(sampler.chain[:, :, 7].T, color="k", alpha=0.4)
axes[7].set_ylabel("$w2$")

#axes[7].plot(sampler.chain[:, :, 7].T, color="k", alpha=0.4)
#axes[7].set_ylabel("$ffunc$")

fig.tight_layout(h_pad=0.0)
fig.savefig("walkers for RV analysis.png")

#%%
##################### getting the Triangle plot #####################################

burnin = 2000
newsamples = sampler.chain[:, burnin:, :].reshape((-1, ndim))

gamma1_same = np.percentile(newsamples[:,0], [50])
gamma2_same = np.percentile(newsamples[:,1], [50])
K1_same = np.percentile(newsamples[:,2], [50])
K2_same = np.percentile(newsamples[:,3], [50])
ecc1_same = np.percentile(newsamples[:,4], [50])
ecc2_same = np.percentile(newsamples[:,5], [50])
w1_same = np.percentile(newsamples[:,6], [50])
w2_same = np.percentile(newsamples[:,7], [50])
#ffunc_same = np.percentile(newsamples[:,7], [50])

fig = corner.corner(newsamples, labels=["$gamma1$","$gamma2$","$K1$","$K2$","$ecc1$","$ecc2$","$w1$","$w2$"])
fig.savefig("line-triangle RV total .png")

#%%
#######################################################################################
############### Plotting the model and the data for the data set###################

##### When you are plotting the model, just take more time values in order to get a smoother plot#####

t14 = [t1[0]] # this is to get a smoother plot

for x in range(1,len(t1)):
    n1 = 20
    tempadd = (t1[x] - t1[x-1])/n1
    for y in range(1,n1):  
        tempa = t1[x-1] + y*tempadd
        t14.append(tempa)
    t14.append(t1[x])
    
t24 = [t2[0]] # this is to get a smoother plot

for x in range(1,len(t2)):
    n = 20
    tempadd = (t2[x] - t2[x-1])/n
    for y in range(1,n):  
        tempa = t2[x-1] + y*tempadd
        t24.append(tempa)
    t24.append(t2[x])
    
t34 = t14 + t24
    
t14 = np.array(t14) ## these are just to get model values at more time values
t24 = np.array(t24)
t34 = np.array(t34)  

####################### Now to bring the data and the model on the same level ###############

f1levelled = []

for x in range(0, len(f1)):
    temp = np.float(gamma2_same - gamma1_same)
    add = f1[x] + temp
    f1levelled.append(add)

f1levelled = np.array(f1levelled)
f2levelled = np.array(f2levelled)
f3levelled = np.concatenate((f1levelled,f2levelled))

#%%
############ the model #########################
modelnet11 = ap.pl_rv_array(t14, 0, K1_same, w1_same, ecc1_same, t01, p1)
modelnet12 = ap.pl_rv_array(t14, 0, K2_same, w2_same, ecc2_same, t02, p2)
t_modelnet1 = modelnet11 + modelnet12 + gamma2_same
    
modelnet21 = ap.pl_rv_array(t24, 0, K1_same, w1_same, ecc1_same, t01, p1)
modelnet22 = ap.pl_rv_array(t24, 0, K2_same, w2_same, ecc2_same, t02, p2)
t_modelnet2 = modelnet21 + modelnet22 + gamma2_same
    
t_modelnet = np.concatenate((t_modelnet1,t_modelnet2))

plt.figure()
plt.plot(t3, f3levelled,'b.',t34, t_modelnet,'r-', label = 'Fit for dataset 1')
#plt.axis([57010, 57140, 7.15, 7.30])
plt.errorbar(t3, f3levelled, yerr = np.array(ferr3))
plt.savefig('without phase folding.png')

###################### Getting the mass for each planet #####################
#%%
Mass_star = 0.949*cst.M_sun.value

def relative_mass(i,k,P,M,e): #All in SI units, returns in terms of earth masses
    return (1/math.sin(i))*(cst.M_sun.value/cst.M_earth.value)*k*1000*((P*24*60*60/(2*np.pi*constnt.gravitational_constant*M))**(1/3))*((1-(e**2))**(1/2))

mass1 = []
mass2 = []
for x in range(0,nwalkers) : #not varying i here
    k1temp = np.float(np.percentile(sampler.chain[:,burnin:,2][x], [50]))
    k2temp = np.float(np.percentile(sampler.chain[:,burnin:,3][x], [50]))
    ecc1temp = np.float(np.percentile(sampler.chain[:,burnin:,4][x], [50]))
    ecc2temp =  np.float(np.percentile(sampler.chain[:,burnin:,5][x], [50]))
    mass1.append(relative_mass(i1,k1temp,p1,Mass_star,ecc1temp))
    mass2.append(relative_mass(i2,k2temp,p2,Mass_star,ecc2temp))
 
mass1_same =   np.float(np.percentile(mass1, [50]))
mass1_upper =  np.float(np.percentile(mass1, [84]) - np.percentile(mass1, [50]))
mass1_lower =  np.float(np.percentile(mass1, [50]) - np.percentile(mass1, [16]))

mass2_same =   np.float(np.percentile(mass2, [50]))
mass2_upper =  np.float(np.percentile(mass2, [84]) - np.percentile(mass2, [50]))
mass2_lower =  np.float(np.percentile(mass2, [50]) - np.percentile(mass2, [16]))

print(mass1_same,mass1_upper,mass1_lower)
print(mass2_same,mass2_upper,mass2_lower)

#mass1 = relative_mass(i1,K1_same,p1,Mass_star,ecc1_same)
#mass2 = relative_mass(i2,K2_same,p2,Mass_star,ecc2_same)

#print(mass1*cst.M_sun.value/cst.M_earth.value)
#print(mass2*cst.M_sun.value/cst.M_earth.value)
#plt.figure()
#plt.plot(t3, f3levelled,'b.',t34, t_modelnet,'r-', label = 'Fit for dataset 1')
#plt.axis([57010, 57140, 7.15, 7.30])
#plt.errorbar(t3, f3, yerr = np.array(ferr3))
##plt.savefig('model with more time part1.png')
#
#plt.figure()
#plt.plot(t3, f3levelled,'b.',t34, t_modelnet,'r-', label = 'Fit for dataset 1')
#plt.axis([57370, 57450, 7.15, 7.40])
#plt.errorbar(t3, f3, yerr = np.array(ferr3))
##plt.savefig('model with more time part2.png')

#plt.figure()
#plt.plot(t2, f2,'b.', label = 'Data2')
#plt.errorbar(t2, f2, yerr = np.array(ferr2))
#plt.savefig('data2.png')