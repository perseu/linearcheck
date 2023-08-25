#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script was created to check the linear response of the SBIG-11000M CCD.
It takes a collection of images taken from a white screen, and performs the median, 
and average of the pixel values of the all image, and then from regions of interest of the CCD.
The results are then plotted. 

Created on Thu Aug 24 12:09:26 2023

@author: jmsaguas

"""

# imports
import numpy as np
import pandas as pd
import os, sys
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.optimize import curve_fit


# Global constants
# CCD regions format [x,y,delta]
regions =[[250,1100,100],[1100,1100,100],[1100,250,100],[250,250,100],[1002,668,100]]



# Global Variables
pathImages = ''
pathTargetRegions = ''
pathResults = ''
language = 'es'             # Options: español='es' and english='en'

argtemp = []
fullList = []

# Functions
def checkRegion(region,data,exptime):
    row=region[0]
    col=region[1]
    delta=region[2]
    regiondata = data[row-delta:row+delta,col-delta:col+delta]
    medianCounts = np.median(regiondata)
    avgCounts = np.average(regiondata)
    return [exptime,medianCounts,avgCounts]

def presentPlots(results, regionsResults, pathResults, totalParams, regionParams):
    
    # Presenting plot of the all CCD.
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot(results['exptime'],lineEquation(results['exptime'], totalParams[0], totalParams[1]), marker='.', color='b',label='Linear Regression')
    ax.plot(results['exptime'],results['medianCounts'], marker='x', color='k',label='Acquired data')
    if language=='es':
        ax.set(xlabel='Tiempo de exposición (s)', ylabel='Cuentas')
    if language=='en':
        ax.set(xlabel='Exposure time (s)', ylabel='Counts')
    plt.legend()
    if language=='es':
        plt.title('Relación entre el tiempo de exposición y el recuento mediano')
    if language=='en':
        plt.title('Relation between Exposure time and Median Count')
    plt.show()

def lineEquation(x,m,b):
    return m*x+b



# If there was a Main, this would be it...
args = sys.argv

# Checking if the user supplied what we need to work.
if len(args) == 1:
    print('This script need parameters...\nSyntax: '+args[0].split('/')[-1]+' i=ImagesPath t=pathToTargetsCSVFile r=pathToResults\n')
else:
    if len(args) > 4:
        print('Too many parameters!!!\nATTENTION!!!\nSyntax: '+args[0].split('/')[-1]+' i=ImagesPath t=pathToTargetsCSVFile r=pathToResults\n')
        exit()
    if len(args) < 4:
        print('Too few parameters!!!\nATTENTION!!!\nSyntax: '+args[0].split('/')[-1]+' i=ImagesPath t=pathToTargetsCSVFile r=pathToResults\n')
        exit()
    if len(args) == 4:
        for ii in range(len(args)):
            argtemp = args[ii].split('=')
            if argtemp[0] == 'i':
                pathImages = argtemp[1]
            if argtemp[0] == 't':
                pathTargetRegions = argtemp[1]
            if argtemp[0] == 'r':
                pathResults = argtemp[1]



# Scanning all subdirectories, above rootDirectory.
for path, subdirs, files in os.walk(pathImages):
    for name in files:
        fullList.append(os.path.abspath(path)+'/'+name)

# Initiating results structure.        
resname = ['exptime','medianCounts','avgCounts']
results = []
regionsResults = {'region1':[],'region2':[],'region3':[],'region4':[],'region5':[]}
regionParams = {'region1':[],'region2':[],'region3':[],'region4':[],'region5':[]}

for fitsfile in fullList:
    hdul = []
    hdul = fits.open(fitsfile)
    exptime = hdul[0].header['EXPTIME']
    data = hdul[0].data
    results.append([exptime,np.median(data),np.average(data)])
    regionsResults['region1'].append(checkRegion(regions[0],data,exptime))
    regionsResults['region2'].append(checkRegion(regions[1],data,exptime))
    regionsResults['region3'].append(checkRegion(regions[2],data,exptime))
    regionsResults['region4'].append(checkRegion(regions[3],data,exptime))
    regionsResults['region5'].append(checkRegion(regions[4],data,exptime))

# storing data in Pandas DataFrames.    
for region in regionsResults.keys():
    regionsResults[region] = pd.DataFrame(regionsResults[region],columns=resname).sort_values('exptime')
resultsDF = pd.DataFrame(results,columns=resname).sort_values('exptime')

# Fitting a curve to the data.
params, cov = curve_fit(lineEquation,resultsDF['exptime'],resultsDF['medianCounts'])
regionParams['region1'] = curve_fit(lineEquation,regionsResults['region1']['exptime'],regionsResults['region1']['medianCounts'])
regionParams['region2'] = curve_fit(lineEquation,regionsResults['region2']['exptime'],regionsResults['region2']['medianCounts'])
regionParams['region3'] = curve_fit(lineEquation,regionsResults['region3']['exptime'],regionsResults['region3']['medianCounts'])
regionParams['region4'] = curve_fit(lineEquation,regionsResults['region4']['exptime'],regionsResults['region4']['medianCounts'])
regionParams['region5'] = curve_fit(lineEquation,regionsResults['region5']['exptime'],regionsResults['region5']['medianCounts'])

# checking for the existance of the results path.
if not os.path.exists(pathResults):
    os.makedirs(pathResults)

presentPlots(resultsDF, regionsResults, pathResults, params, regionParams)

print('This is the end... TumTumTum My lonely friend... the end...\n')