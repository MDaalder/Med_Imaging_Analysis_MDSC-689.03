#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:21:30 2020

@author: MattD
"""

import vtk
import os
import sys
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

imageFile = 'headGaussian.nii'


inputReader = vtk.vtkNIFTIImageReader()
inputReader.SetFileName(imageFile)
inputReader.Update()

inputImage = inputReader.GetOutput()

imageName = inputReader.GetFileName()
outfile = str(os.path.splitext(imageName)[0]) + '_GaussianSmoothed.nii'
outpath = os.path.join(os.getcwd(), outfile)

print('\nOutfile:  ' + outfile)
print('\nOutpath:  ' + outpath + '\n')

# make a copy of the input image(s) to work with and maintain original data
copyImage = vtk.vtkImageData()
copyImage.DeepCopy(inputReader.GetOutput()) 

# get the image dimensions
imageDim = inputImage.GetDimensions()
print("imagedim= " + str(imageDim))
imageExt = inputImage.GetExtent()
print("image extents= " + str(imageExt))
print("length of image ext= " + str(len(imageExt)))
kernelSize = 3 # could make this an input arg in the future

imageDimMin = np.empty(3, dtype = int) # will have the starting coordinates for the image we want to smooth (padded)
imageDimMax = np.empty(3, dtype = int) # will have the ending coordinates for the images we want to smooth (padded)

# dummy variables
a = 0
b = 0

# set up the dimenions of the image we are analyzing to help iterate over the image's data
# accounts for the size of the smoothing kernel (i.e. implementing padding)
for i in range(0,len(imageExt),2): # 0 to 4 by twos to get all even numbers, corresponds to x y z min coords   
    imageDimMin[a] = imageExt[i]+(kernelSize - kernelSize//2) # creates a list of the image's min coordinates to start smoothing from
    a += 1
for i in range(1,(len(imageExt)+1),2): # 1 to 5 by twos to get all uneven numbers, corresponds to x y z max coords
    imageDimMax[b] = imageExt[i]-(kernelSize - kernelSize//2) # creates a list of the image's max coordinates to stop smoothing at
    b += 1

print("image dim min, max= " + str(imageDimMin) + str(imageDimMax))

# 3D Gaussian kernel, hard coded
# eventually change this to match the size of the array requested i.e. 3x3, 5x5, etc
kernel = np.array([[[1, 2, 1], [2, 4, 2], [1, 2, 1]], 
                   [[2, 4, 2], [4, 16, 4], [2, 4, 2]], 
                   [[1, 2, 1], [2, 4, 2], [1, 2, 1]]])

# kernelNormal normalizes each entry in the array. If all normalized entries are summed, the answer is 1.0
kernelNormal = kernel/np.sum(kernel)

# Set up a numpy array to fill with image data. 
# Will use this to get smoothed, filtered values.
# imageArray = np.empty((imageDim[0], imageDim[1], imageDim[2]), dtype=float)

""" need to fill the imageArray with values from inputImage"""

# Itereate over all admissiblie pixels in a given image    
for x in range(imageDimMin[0], imageDimMax[0]):#image.GetDimensions()[0]):
    for y in range(imageDimMin[1], imageDimMax[1]):#image.GetDimensions()[1]):
        for z in range(imageDimMin[2], imageDimMax[2]):#image.GetDimensions()[2]):
            
            # subArray = an extracted value from the imageArray, should be 3x3x3 like the kernel
            subArray = np.empty((kernelSize, kernelSize, kernelSize), dtype=float)
            
            # iterate through values to append to the subArray based on 3x3x3 filter
            # can change the numbers so it isn't hard coded
            l=0 # dummy i index value
            for i in range(x-1, x+2):
                m=0 # dummy j index value
                l+=1
                for j in range(y-1, y+2):
                    n=0 # dummy k index value
                    m+=1
                    for k in range(z-1, z+2):
                        n+=1
                        voxelValue = inputImage.GetScalarComponentAsFloat(i, j, k, 0)
                        """subArray is a numpy array and needs to be a vtk object to work"""
                        # subArray.SetScalarComponentAsFloat((l-1), (m-1), (n-1), voxelValue)
                        subArray[l-1][m-1][n-1] = voxelValue
            
            # gives the value of the central voxel by summing all the values from the kernelNormal*subArray convolution
            # this is the blurring or smoothing step
            voxelBlurred = np.sum(kernelNormal*subArray)
            
            # voxelValue = inputImage.GetScalarComponentAsFloat(x,y,z,0) #inputReader or inputImage????
            copyImage.SetScalarComponentFromFloat(x, y, z, 0, voxelBlurred)



# test = np.array([[[1, 2, 3], [4, 5, 6], [7, 8, 9]], 
#                    [[10, 11, 12], [13, 14, 15], [16, 17, 18]], 
#                    [[21, 22, 23], [24, 25, 26], [27, 28, 29]]])

    
    # write the new smoothed image
    # do I need an intermediate step to save all the filtered data in memory as it's being made before writing it?
    # do I want to save a new 'physical' file, or just keep the information in memore to display?
    
    # smoothImage = vtk.vtkWriter
    
"""
#check code below for voxel navigation and value modification
for x in range(0, image.GetDimensions()[0]):
    for y in range(0, image.GetDimensions()[1]):
        for z in range(0, image.GetDimensions()[2]):
            voxelValue = image.GetScalarComponentAsFloat(x,y,z,0)
            image.SetScalarComponentFromFloat(x, y, z, 0, voxelValue)

"""