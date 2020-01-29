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

    
# 3D Gaussian kernel # do I have to divide by the sum of the matrix elements to normalize? i.e. 16
kernel = np.array([[[1, 2, 1], [2, 4, 2], [1, 2, 1]], 
                   [[2, 4, 2], [4, 16, 4], [2, 4, 2]], 
                   [[1, 2, 1], [2, 4, 2], [1, 2, 1]]])

# kernelNormal normalizes each entry in the array. If all normalized entries are summed, the answer is 1.0
kernelNormal = kernel/np.sum(kernel)

# gives the value of the central voxel by summing all the values from the kernelNormal*imageArray convolution
# this is the blurring or smoothing step
voxelBlur = np.sum(kernelNormal*imageArray)


    
for x in range(0, image.GetDimensions()[0]):
    for y in range(0, image.GetDimensions()[1]):
        for z in range(0, image.GetDimensions()[2]):
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