#!/usr/bin/env python3

"""
MDSC 689.03
Assignment #2: Applying Gaussian and Median filters

inputs:
    >>>python codename.py arg_1 arg_2 arg_3
    arg_1: path to DICOM folder or NIFTI image
    arg_2: type of filter to apply. Takes "gaussian" or "median"
    arg_3: Size of kernel to apply. Takes uneven int (i.e. 3 or 5 or 7...)
        arg_2 not fully implemented. Only input "3"
    Example:
        >>>python codename.py headGaussian.nii gaussian 3
        
Other inputs: 
    when prompted, a path to a NIFTI image or DICOM image directory
    these images do NOT need to be in the working directory
    Make sure there are no spaces in the path name

This code will filter and display a single set of DICOM or NIFTI 
medical images independent of the Python working directory.
It will also write a new filtered image as NIFTI file type to the working directory.

Last edited on Feb 01 2020
# -*- coding: utf-8 -*-

@author: MattD

"""

#import packages required
import vtk   
import os
import sys
import numpy as np

# Argument variables to use throughout code
imageFile = sys.argv[1]
filterType = str(sys.argv[2])
kernelSize = int(sys.argv[3])
  
# =============================================================================
# Prompts the user for the file location of the images to read
# Checks to see if the file or directory is useable
# Returns the useable path of the file (NIFTI) or directory (DICOM) to use as a reader
# This allows the location of the file(s) used to be independent of the working directory
# =============================================================================
def readImages(imageFile):
    
    # dummy variable to run the while loop
    find = True
    
    # define the variables to determine the location of DICOM directory or NIFTI file
    while find == True:
        
        #global imageFile
       # imageFile = input("Please input nifti file path or DICOM folder path.\n", 
       #                   "Make sure there are no spaces in the path (inadmissibile character.\n" )
        
        if os.path.isdir(imageFile):
            print("Using " + os.path.basename(imageFile) + ' as directory to read from')
        elif os.path.exists(imageFile):
            print("Using " + os.path.splitext(imageFile)[0] + ' as image to read')
        else:
            imageFile = 'headGaussian.nii'
            print("Inappropriate input. Using " + imageFile + ' as default.')
            
        if (not os.path.exists(imageFile)):
        	print("ERROR: " + imageFile + " does not exist!")
        	sys.exit()
        
        # asserts this is a directory appropriate for DICOM reading
        if (os.path.isdir(imageFile)):
        	reader = vtk.vtkDICOMImageReader()
        	reader.SetDirectoryName(imageFile)
        # asserts this is a file appropriate for nifti reading
        else:
        	ext = os.path.splitext(imageFile)[1]
        	if (ext == ".nii" or ext == ".nifti"):
        		reader = vtk.vtkNIFTIImageReader()
        		reader.SetFileName(imageFile)
        	else:
        		print("ERROR: image format not recognized for " + imageFile)
        		sys.exit()
        
        
        reader.Update()
        
        find = False
            
    return (reader)


# =============================================================================
# Display everything in vtk window.
# Includes information about image slice and image windowing.
#
# Input: an intialised vtkImageReader object 
# 
# Eventual wants: display patient id, patient position, and automatic center positioning of medical images 
# =============================================================================
def displayImages(reader):  
    
    # Gets all image data
    imageData = reader.GetOutput()
    
    # Extracting the dimensions of the image 
    coordBounds = imageData.GetDimensions() # this gives maxx, maxy, maxz coordinate numbers
    
    # assigning dimension variables in case want to use for sizing and positioning actors and windows   
    # in the future, would want to assign location and sizing of objects by local screen resolution
    xdim = int(coordBounds[0])
    ydim = int(coordBounds[1])
    zdim = int(coordBounds[2])
    
    # initialise the mapper. The image displayed will be the middle image in the image set
    mapper = vtk.vtkImageMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.SetZSlice(int(zdim/2))
    mapper.SetColorWindow(1000)
    mapper.SetColorLevel(600)
    
    # create the actor
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    actor.SetPosition(100, 170)
    
    # assign text to display: current slice and window level and color level
    outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                  'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
    
    # create text actor
    txt = vtk.vtkTextActor()
    txt.SetInput(outputText1)
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(30)
    txtprop.SetColor(1,1,1)
    txt.SetDisplayPosition(10,30)
    
    # create second text actor
    infoText = vtk.vtkTextActor()
    infoText.SetInput("Scroll up or down to navigate through the slices. \n")
    infotxtprop=infoText.GetTextProperty()
    infotxtprop.SetFontFamilyToArial()
    infotxtprop.SetFontSize(20)
    infotxtprop.SetColor(1,1,1)
    infoText.SetDisplayPosition(10, 15)
    
    # create the renderer
    ren = vtk.vtkRenderer()
    
    # create the render window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(800, 700)
    
    # Connect an interactor to the image viewer
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleImage())
    
    # function to change projected image slice with key press            
    # Add observers for mouse wheel events to scroll through slices
    def wheelForward(obj, event):
        zSlice = mapper.GetZSlice()
    	
        if (zSlice < mapper.GetWholeZMax()):
            mapper.SetZSlice(zSlice + 1)
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                       'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
        txt.SetInput(outputText1)
            
    def wheelBackward(obj, event):
        zSlice = mapper.GetZSlice()
        
        if (zSlice > mapper.GetWholeZMin()):
            mapper.SetZSlice(zSlice - 1)
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                       'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n')
        txt.SetInput(outputText1)    
    
    # add the scrolling events to move through slices    
    iren.AddObserver("MouseWheelForwardEvent", wheelForward)
    iren.AddObserver("MouseWheelBackwardEvent", wheelBackward)
    
    # add the actors to the renderer
    ren.AddActor(actor)
    ren.AddActor(txt)
    ren.AddActor(infoText)
    
    # initialise the interactor
    iren.Initialize()
    
    # render the scene with all actors in it
    renWin.Render()
    
    # Start the event loop for the interactor
    iren.Start()
    
    return()

# =============================================================================
# Apply a smoothing or blurring filter to a desired image.
# Input is a vtk reader initialized medical image of type DICOM or NIFTI
# Outputs an updated vtk reader object and writes a new filtered image as NIFTI filetype
# =============================================================================
def filterSmooth(inputReader):
    
    inputImage = inputReader.GetOutput()
    
    imagePath = imageFile
    
    # determes the filename for the output file based on filter type and input
    if (os.path.isdir(imagePath)) and filterType == "gaussian":
#        outfile = "Thorax_GaussianSmoothed"
        outfile = str(os.path.basename(imagePath)) + '_GaussianSmoothed.nii'
    elif (os.path.isdir(imagePath)) and filterType == "median":
#        outfile = "Thorax_MedianSmoothed"
        outfile = str(os.path.basename(imagePath)) + '_MedianSmoothed.nii'
    elif filterType == "gaussian":
        outfile = str(os.path.splitext(imagePath)[0]) + '_GaussianSmoothed.nii'
    elif filterType == "median":
        outfile = str(os.path.splitext(imagePath)[0]) + '_MedianSmoothed.nii'
        
    ## used for debugging
    # outpath = os.path.join(os.getcwd(), outfile)
    # print('\nOutfile:  ' + outfile)
    # print('\nOutpath:  ' + outpath + '\n')
    
    # make a copy of the input image(s) to work with and maintain original data
    copyImage = vtk.vtkImageData()
    copyImage.DeepCopy(inputReader.GetOutput()) 
    
    # get the image dimensions
    imageDim = inputImage.GetDimensions()
    imageExt = inputImage.GetExtent()

    kernelSize = 3 # could make this an input arg in the future
    
    imageDimMin = np.empty(3, dtype = int) # will have the starting coordinates for the image we want to smooth (padded)
    imageDimMax = np.empty(3, dtype = int) # will have the ending coordinates for the images we want to smooth (padded)
    
    ## used for debugging
    # print("imagedim= " + str(imageDim))
    # print("image extents= " + str(imageExt))
    # print("length of image ext= " + str(len(imageExt)))
    
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
    
    ## used for debugging
    # print("image dim min, max= " + str(imageDimMin) + str(imageDimMax))
    
    # 3D Gaussian kernel, hard coded. Eventually change this to match the size of the array requested i.e. 3x3, 5x5, etc
    kernel = np.array([[[1, 2, 1], [2, 4, 2], [1, 2, 1]], 
                       [[2, 4, 2], [4, 16, 4], [2, 4, 2]], 
                       [[1, 2, 1], [2, 4, 2], [1, 2, 1]]])
    
    # kernelNormal normalizes each entry in the array. If all normalized entries are summed, the answer is 1.0
    # will be used as the gaussian kernel for fitering
    kernelNormal = kernel/np.sum(kernel)

    # used for testing to speed up processing. Set start and end Z-Slices to filter.
    imageDimMin[2] = 120
    imageDimMax[2] = 130
    
    # Itereate over all admissiblie pixels in a given image    
    for x in range(imageDimMin[0]-1, imageDimMax[0]+1):
        for y in range(imageDimMin[1]-1, imageDimMax[1]+1):
            for z in range(imageDimMin[2]-1, imageDimMax[2]):
                
                # a sub array of the image being filtered. Should be the size of the kernel
                subArray = np.empty((kernelSize, kernelSize, kernelSize), dtype=float)
                
                # iterate through values to append to the subArray based on 3x3x3 filter
                # the created sub array is composed to original image values and will be used to
                # apply the kernel to, and determine the filtered voxel value(s)
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
                            subArray[l-1][m-1][n-1] = voxelValue
                
                if filterType == "gaussian":
                    # gives the value of the central voxel by summing all the values from the kernelNormal*subArray convolution
                    # this is the gaussian blurring or smoothing step
                    voxelBlurred = np.sum(kernelNormal*subArray)
                    copyImage.SetScalarComponentFromFloat(x, y, z, 0, voxelBlurred)
                elif filterType == "median":
                    # gives the value of the central voxel by determining the median value of the subArray
                    # this is the median blurring or smoothing step
                    voxelMedian = np.median(subArray)
                    copyImage.SetScalarComponentFromFloat(x, y, z, 0, voxelMedian)
                
               # print('. ')

    # write the new filtered image as a NIFTI filetype to the working directory
    # I'm not sure how to do this for DICOM
    writer = vtk.vtkNIFTIImageWriter()
    writer.SetFileName(outfile)
    writer.SetInputData(copyImage)
    writer.Write()
    
    # updates the vtk reader to the new filtered image
    smoothedImage = vtk.vtkNIFTIImageReader()
    smoothedImage.SetFileName(outfile)
    smoothedImage.Update()
    
    return(smoothedImage)


reader = readImages(imageFile)
readerSmoothed = filterSmooth(reader)

displayImages(readerSmoothed)
    