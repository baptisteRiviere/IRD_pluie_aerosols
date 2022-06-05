# -*- coding: utf-8 -*-
"""
Created on Mon May 31 15:24:41 2021

@author: utilisateur
"""

#%% IMPORTS AND FUNCTIONS

import os, glob, shutil
import numpy as np
import numpy.ma as ma
#from sklearn.metrics import r2_score
import pandas as pd
import matplotlib.pyplot as plt

def get_AOT(array, subset):
    
    if subset == 'French Guiana':
        extent = [-55, -50, 2, 6]
        subset = np.where(lons > extent[0], array, np.nan)  # highest coordonate
        subset = np.where(lons < extent[1], subset, np.nan) # lowest coordonate
        subset = np.where(lats < extent[3], subset, np.nan) # lowest latitude
        subset = np.where(lats > extent[2], subset, np.nan) # highest latitude
        array_values = subset[~subset.mask]
        print("French Guiana AOT values : ", array_values)
        print("Max of AOT value in the area : ",  np.nanmax(array_values))
        print("Mean of AOT value in the area : ", np.nanmean(array_values))
        return array_values
        
    if subset == 'Cayenne':
        extent = [-52.5, -52, 4.5, 5]
        subset = np.ma.masked_where(lons > extent[1], array) # highest coordonate
        subset = np.ma.masked_where(lons < extent[0], subset) # lowest coordonate 
        subset = np.ma.masked_where(lats < extent[2], subset) # lowest latitude
        subset = np.ma.masked_where(lats > extent[3], subset) # highest coordonate
        array_values = subset[~subset.mask]
        print("Cayenne AOT values : ", array_values)
        print("Max of AOT value in the area : ",  np.ma.max(array_values))
        print("Mean of AOT value in the area : ", np.ma.mean(array_values))
        return array_values
        
    if subset == 'Kourou':
        extent = [-52.95, -52.35, 4.85, 5.45]
        subset = np.ma.masked_where(lons > extent[1], array) # highest coordonate
        subset = np.ma.masked_where(lons < extent[0], subset) # lowest coordonate 
        subset = np.ma.masked_where(lats < extent[2], subset) # lowest latitude
        subset = np.ma.masked_where(lats > extent[3], subset) # highest coordonate
        array_values = array[~subset.mask]
        print("Kourou AOT values : ", array_values)
        print("Max of AOT value in the area : ",  np.ma.max(array_values))
        print("Mean of AOT value in the area : ", np.ma.mean(array_values))
        return array_values
    
    if subset == 'Matoury':
        extent = 'I don t know yet.'
        subset = np.ma.masked_where(lons > extent[1], array) # highest coordonate
        subset = np.ma.masked_where(lons < extent[0], subset) # lowest coordonate 
        subset = np.ma.masked_where(lats < extent[2], subset) # lowest latitude
        subset = np.ma.masked_where(lats > extent[3], subset) # highest coordonate
        array_values = array[~subset.mask]
        print("Matoury AOT values : ", array_values)
        print("Max of AOT value in the area : ",  np.ma.max(array_values))
        print("Mean of AOT value in the area : ", np.ma.mean(array_values))
        return array_values
        
    if subset == 'Saint-Georges':
        extent = [-52.5, -52, 3.25, 3.75]
        subset = np.ma.masked_where(lons > extent[1], array) # highest coordonate
        subset = np.ma.masked_where(lons < extent[0], subset) # lowest coordonate 
        subset = np.ma.masked_where(lats < extent[2], subset) # lowest latitude
        subset = np.ma.masked_where(lats > extent[3], subset) # highest coordonate
        array_values = array[~subset.mask]
        print("Saint-Georges AOT values : ", array_values)
        print("Max of AOT value in the area : ",  np.ma.max(array_values))
        print("Mean of AOT value in the area : ", np.ma.mean(array_values))
        return array_values
    
    if subset == 'Guadeloupe':
        extent = [-61, -62, 15.75, 16.75]
        subset = np.ma.masked_where(lons > extent[1], array) # highest coordonate
        subset = np.ma.masked_where(lons < extent[0], subset) # lowest coordonate 
        subset = np.ma.masked_where(lats < extent[2], subset) # lowest latitude
        subset = np.ma.masked_where(lats > extent[3], subset) # highest coordonate
        array_values = array[~subset.mask]
        print("Guadeloupe AOT values : ", array_values)
        print("Max of AOT value in the area : ",  np.ma.max(array_values))
        print("Mean of AOT value in the area : ", np.ma.mean(array_values))
        return array_values
    
    else : 
        print('Subset not included in the function or not well spelled.')

def plot(array, title):
    """
    TO DELETE AFTER.

    """
    import matplotlib.pyplot as plt
    plt.imshow(array)
    plt.colorbar()
    plt.title(title)
    plt.show()
    
def open_bin(binFile):
    """
    Open .high.bin file after being decompressed (gz) with PowerISO software.

    Parameters
    ----------
    
    binFile : str
        FILENAME CONDUCTING TO THE .BIN FILE

    Returns
    -------
    aot_edr : numpy array
        ARRAY CONTAINING AOT VALUES.
    nAOT : numpy array
        ARRAY CONTAINING NUMBER OF PIXELS USED TO COMPUTE AOT MEAN IN THE GRID BOX.

    """
    
    #open .high.bin file
    imnp = np.fromfile(binFile, dtype = np.single) # type : single precision float
    imnp2 = np.fromfile(binFile, dtype = np.int_) # type : long integer
    ##NB : the data is contained in the same matrix array use to open the data
    ##NB2 : note that there are 2 073 600 cells which, divided by 2,
    ##corresponds to the 1 036 800 cells as described in the readme text.
    
    # reshape arrays
    array = np.reshape(imnp, [int(len(imnp)/1440), 1440])
    # array = np.flipud(array)
    array2 = np.reshape(imnp2, [int(len(imnp)/1440), 1440])
    # array2 = np.flipud(array2)
    aot_edr = array[:720, :1440] # cut the principal arrays
    n_aot_edr = array2[720:, :1440] # cut the principal array
    
    # mask invalid values
    aot_edr = ma.masked_where(aot_edr > 5, aot_edr) # mask aberrant values
    aot_edr = ma.masked_where(aot_edr < -100, aot_edr) # mask invalid values
    n_aot_edr = ma.masked_where(n_aot_edr > 100, n_aot_edr) # mask invalid values
    
    return aot_edr, n_aot_edr
    
def LonLat():
    """
    Create longitudes and latitudes arrays of the Gridded AOT EDR 550 nm data.

    Returns
    -------
    lats : array
        ARRAY OF LATITUDES OF SHAPE (720, 1440).
    lons : array
        ARRAY OF LONGITUDES OF SHAPE (720, 1440).
    """
    resolution = 0.25
    minLon = -179.875  
    maxLon =  179.875 
    minLat =  -89.875
    maxLat =   89.875
    
    lon = np.arange(minLon, maxLon+0.25, resolution) # create an horizontal matrix between -180 to 180 each 0.25
    lons = np.tile(lon, (720,1)) # clone column 720 times 
    lat = np.arange(minLat, maxLat+0.25, resolution)[:, np.newaxis] # create an vertical matrix between -90 to 90 each 0.25
    lats = np.tile(lat, (1,1440)) # clone line 1440 times
        
    return lons, lats

def retrieve_PointCoordinates(lons, lats, Lat, Lon):
    """
    Retrieve the position x, y in the matrix for the given geographic coordinates.

    Parameters
    ----------
    lons : array
        ARRAY OF LONGITUDES OF THE WHOLE GRIDDED AOT EDR 550 NM PRODUCTS.
    lats : array
        ARRAY OF LATITUDES OF THE WHOLE GRIDDED AOT EDR 550 NM PRODUCTS.
    Lat : float
        LATITUDE OF THE POINT OF INTEREST.
    Lon : float
        LONGITUDE OF THE POINT OF INTEREST.

    Returns
    -------
    x : int
        POSITION FOR GIVEN LATITUDE POINT.
    y : int
        POSITION FOR GIVEN LONGITUDE POINT.
    """
    
    #retreive possible x positions in the matrix
    x_list = []
    for x in range(lats.shape[0]-1):
        if Lat-0.25 < lats[x,0] < Lat+0.25:
            x_list.append(x)
        else:
            pass
    
    #retrieve possible y positions in the matrix
    y_list = []
    for y in range(lons.shape[1]-1):
        if Lon-0.25 < lons[0,y] < Lon+0.25:
            y_list.append(y)
        else:
            pass
        
    for x in x_list :
        x = min(x_list, key=lambda x:abs(x-Lat))
        
    for y in y_list: 
        y = min(y_list, key=lambda y:abs(y-Lon))
        
    return x, y
            
def axes3_plot(x, y1, y2, title):
    """
    Plot two products (y1,y2) according to x abscisse.

    Parameters
    ----------
    x : list or array
        ABSCISSE OF THE SCATTER PLOT.
    y1 : list or array
        DATA TO PLOT.
    y2 : list or array
        SECOND DATA TO SCATTER PLOT.
    title : str
        TITLE OF THE GRAPH.

    Returns
    -------
    fig : figure
        GRAPH OF 3 AXES SCATTERING TWO DIFFERENT DATA.

    """
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.scatter(x, y1, c='b')
    ax2.scatter(x,y2, c='r', marker = "x")
    
    ax1.set_ylabel("Gridded AOT EDR 550 nm")
    ax2.set_ylabel("n AOT EDR 550 nm")
    ax1.legend("AOT")
    ax2.legend("n AOT")
    ax1.tick_params(axis='x', rotation=45)
    plt.title(title)
    plt.show()
    
    return fig

def polyfit(x, y, degree):

    coeffs = np.polyfit(x, y, degree)
    #Polynomial Coefficients
    polynomial = coeffs.tolist()
    #r-squared
    p = np.poly1d(coeffs)
    #fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    r_squared = ssreg / sstot

    return polynomial, r_squared

def scatterPlot(x, y, title, save_name, data_source, r2, polynomial):
    
    plt.scatter(x,y) # scatter AOT EDR and in-situ measurements of PM10 
    plt.plot(x, polynomial[0]*x+polynomial[1], "g--")
    plt.title(title) # set a title
    # plt.xlim((0,1)) # set x limits
    # plt.ylim((0,1)) # set y limits
    plt.xlabel("Gridded AOT EDR 550 nm \n 'R2: ' %s"%(str(r2)))
    plt.ylabel("in-situ PM10 FROM %s"%(data_source))
    plt.show() # display the graph
    plt.savefig(save_name) # save the figure in the new working directory
    
def df_concat(df1,df2,df3,df4):
    
    arrays2add = np.append(df4, df3, axis=0) # append dataframe to an array
    arrays2add  = np.append(arrays2add, df2, axis=0)
    dd = np.append(arrays2add, df1, axis=0) # name  the new array containing all AOT EDR values (from all classes) according to station name
    dd = pd.DataFrame(dd) # convert the array to dataframe
    
    return dd

def nAOT_r2(df_nAOT_correl):
    
    array = df_nAOT_correl.to_numpy()
    max_r2 = np.nanmax(array[:,1])   
    for i in range(array.shape[0]):
        if array[i,1] == max_r2:
            nAOT = array[i,0]
            
    return nAOT, max_r2