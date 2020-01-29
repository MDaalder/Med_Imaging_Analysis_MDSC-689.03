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

inputImageData = inputReader.GetOutput()

imageName = inputReader.GetFileName()
outfile = str(os.path.splitext(imageName)[0]) + '_GaussianSmoothed.nii'
outpath = os.path.join(os.getcwd(), outfile)

print('\nOutfile:  ' + outfile)
print('\nOutpath:  ' + outpath + '\n')

# make a copy of the input image(s) to work with and maintain original data
copyImage = vtk.vtkImageData()
copyImage.DeepCopy(inputReader.GetOutput()) 

# get the image dimensions
imageDim = inputImageData.GetDimensions()
print(imageDim)
imageExt = inputImageData.GetExtent()
print(imageExt)
print(len(imageExt))
kernelDim = 3 # could make this an input arg in the future

imageDim = np.empty(len(imageExt), dtype=int)
# imageDimMin = np.empty(3, dtype = int)
# imageDimMax = np.empty(3, dtype = int)


for i in range(0, len(imageDim)):
    imageDim[i] = imageExt[i] + 1

# for i in range(0,len(imageExt),2): # 0 to  by twos (gets all even numbers for x y z min coords)
#     imageDimMin[i] = imageExt[i]+1
# for i in range(1,(len(imageExt)+1),2): # 1 to 5 by twos to get all uneven numbers for x y z max coords
#     imageDimMax[i] = imageExt[i]-1

print(imageDim)

# 3D Gaussian kernel
kernel = np.array([[[1, 2, 1], [2, 4, 2], [1, 2, 1]], 
                   [[2, 4, 2], [4, 16, 4], [2, 4, 2]], 
                   [[1, 2, 1], [2, 4, 2], [1, 2, 1]]])

# kernelNormal normalizes each entry in the array. If all normalized entries are summed, the answer is 1.0
kernelNormal = kernel/np.sum(kernel)




    
for x in range(0, image.GetDimensions()[0]):
    for y in range(0, image.GetDimensions()[1]):
        for z in range(0, image.GetDimensions()[2]):
            
            
            # gives the value of the central voxel by summing all the values from the kernelNormal*imageArray convolution
            # this is the blurring or smoothing step
            voxelBlur = np.sum(kernelNormal*imageArray)
            
            
            voxelValue = image.GetScalarComponentAsFloat(x,y,z,0)
            image.SetScalarComponentFromFloat(x, y, z, 0, voxelValue)

# test = np.array([[[1, 2, 1], [2, 4, 2], [1, 2, 1]], 
#                    [[2, 4, 2], [4, 16, 4], [2, 4, 2]], 
#                    [[1, 2, 1], [2, 4, 2], [1, 2, 1]]])

    
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