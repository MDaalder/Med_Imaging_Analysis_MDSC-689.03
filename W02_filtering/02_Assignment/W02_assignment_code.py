#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 16:15:40 2020

@author: MattD
"""


    

    #check code below for voxel navigation and value modification
    for x in range(0, image.GetDimensions()[0]):
        for y in range(0, image.GetDimensions()[1]):
            for z in range(0, image.GetDimensions()[2]):
                voxelValue = image.GetScalarComponentAsFloat(x,y,z,0)
                image.SetScalarComponentFromFloat(x, y, z, 0, voxelValue)
                
    
    # used to create a copy of an image. Remember to set the value of image                
    copyImage = vtk.vtkImageData()
    copyImage.DeepCopy(image)
    
    
    # 3D Gaussian kernel
    kernel = [[[1, 2, 1], [2, 4, 2], [1, 2, 1]], 
              [[2, 4, 2], [4, 16, 4], [2, 4, 2]], 
              [[1, 2, 1], [2, 4, 2], [1, 2, 1]]]
    
    