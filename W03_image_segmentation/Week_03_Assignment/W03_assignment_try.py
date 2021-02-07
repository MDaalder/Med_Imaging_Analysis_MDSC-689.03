#!/usr/bin/env python3

"""
MDSC 689.03
Assignment #3: Segmentation and Dilation/Erosion

inputs:
    >>>python codename.py arg_1 arg_2 arg_3 arg_4 arg_5 arg_6
    arg_1: path to DICOM folder or NIFTI image
    arg_2: type of filter to apply. Takes "gaussian" or "median" or "none"
    arg_3: global thresholding values to use. Input as a list: [x, y]
    arg_4: type of operation to make to the segmentation: 'dilation' 'erosion' 'none' 'close' or 'open'
    arg_5: how many iterations of the operation to implement. Must be an integer.
    Example:
        >>>python W03_assignment_try.py C:/Users/mattd/Documents/GitHub/MDSC-689.03/W01_vtk_intro/W01_Assignment/NIFTI/head.nii gaussian 0 100 close 2
        
Other inputs: 
    when prompted, a path to a NIFTI image or DICOM image directory
    these images do NOT need to be in the working directory
    Make sure there are no spaces in the path name

This code will filter and display a single set of DICOM or NIFTI 
medical images independent of the Python working directory with a segmentation
over top of it. The code will also write a new filtered image as NIFTI file 
type to the working directory so you can access it in the future.


Last edited on Feb 08 2020
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
lowThresh = int(sys.argv[3])
upperThresh = int(sys.argv[4])
operation = str(sys.argv[5])
iterations = int(sys.argv[6])


# imageFile = "C:/Users/mattd/Documents/GitHub/MDSC-689.03/W01_vtk_intro/W01_Assignment/NIFTI/head.nii"
# filterType = 'gaussian'
# kernelSize = int(sys.argv[3])
kernelSize = 3

colorWindow = 1000
colorLevel = 200

# set threshold values for segmentation
# lines body cavities
# lowThresh = -600
# upperThresh = -170

# implement the segmentation image object to be updated as the code runs
segmentationImage = vtk.vtkPassThroughFilter()
  
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
    mapper.SetColorWindow(colorWindow)
    mapper.SetColorLevel(colorLevel)
    
    # create the actor
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    actor.SetPosition(100, 170)
    
    # determine how to visualize the binary segmentation image
    # to overlay on the original medical image(s)
    lookupTable = vtk.vtkLookupTable()
    lookupTable.SetNumberOfTableValues(2)
    lookupTable.SetRange(0., 1.)
    lookupTable.SetTableValue(0, 0., 0., 0., 0.)
    lookupTable.SetTableValue(1, 0., 1., 0., 1.)
    lookupTable.Build()
      
    mapToColors = vtk.vtkImageMapToColors()
    mapToColors.SetLookupTable(lookupTable)
    mapToColors.PassAlphaToOutputOn()
    mapToColors.SetInputData(segmentationImage.GetOutput())
    mapToColors.Update()
    
    # initialise the segmented image mapper
    segMapper = vtk.vtkImageMapper()
    segMapper.SetInputConnection(mapToColors.GetOutputPort())
    segMapper.SetZSlice(mapper.GetZSlice())
    segMapper.SetColorWindow(1)
    segMapper.SetColorLevel(1)
    
    # create the segmented actor
    segActor = vtk.vtkActor2D()
    segActor.SetMapper(segMapper)
    segActor.SetPosition(actor.GetPosition())
    
    
    # assign text to display: current slice and window level and color level
    outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                  'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n'
                  'Lower Threshold: ' + str(lowThresh) + '  Upper Threshold: ' + str(upperThresh))
    
    # create text actor
    txt = vtk.vtkTextActor()
    txt.SetInput(outputText1)
    txtprop=txt.GetTextProperty()
    txtprop.SetFontFamilyToArial()
    txtprop.SetFontSize(30)
    txtprop.SetColor(1,1,1)
    txt.SetDisplayPosition(10,40)
    
    # create second text actor
    infoText = vtk.vtkTextActor()
    infoText.SetInput("Scroll up or down to navigate through the slices. \n")
    infotxtprop=infoText.GetTextProperty()
    infotxtprop.SetFontFamilyToArial()
    infotxtprop.SetFontSize(20)
    infotxtprop.SetColor(1,1,1)
    infoText.SetDisplayPosition(10, 0)
    
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
            segMapper.SetZSlice(mapper.GetZSlice())
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                       'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n'
                       'Lower Threshold: ' + str(lowThresh) + '  Upper Threshold: ' + str(upperThresh))
        txt.SetInput(outputText1)
            
    def wheelBackward(obj, event):
        zSlice = mapper.GetZSlice()
        
        if (zSlice > mapper.GetWholeZMin()):
            mapper.SetZSlice(zSlice - 1)
            segMapper.SetZSlice(mapper.GetZSlice())
        
        # update displayed text
        outputText1 = ("Current slice: " + str(mapper.GetZSlice() + 1) + " of " + str(zdim) + '\n'
                       'Window level: ' + str(int(mapper.GetColorWindow())) + ' Color level: ' + str(int(mapper.GetColorLevel())) + '\n'
                       'Lower Threshold: ' + str(lowThresh) + '  Upper Threshold: ' + str(upperThresh))
        txt.SetInput(outputText1)    
    
    # add the scrolling events to move through slices    
    iren.AddObserver("MouseWheelForwardEvent", wheelForward)
    iren.AddObserver("MouseWheelBackwardEvent", wheelBackward)
    
    # add the actors to the renderer
    ren.AddActor(actor)
    ren.AddActor(segActor)
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
    
    # Filter the image with Gaussian or Median filter
    if filterType == 'gaussian':
        filter_image = vtk.vtkImageGaussianSmooth()
        filter_image.SetInputConnection(inputReader.GetOutputPort())
        filter_image.SetStandardDeviation(1)
        filter_image.SetRadiusFactors(1,1,1)
        filter_image.SetDimensionality(3)
        filter_image.Update()
    
    elif filterType == 'median':
        filter_image = vtk.vtkImageMedian3D()
        filter_image.SetInputConnection(inputReader.GetOutputPort())
        filter_image.SetKernelSize(3,3,3)
        filter_image.Update()
    
    elif filterType == 'none':
        filter_image = reader
    
    copyImage = vtk.vtkImageData()
    copyImage.DeepCopy(filter_image.GetOutput())
    
    if filterType == 'gaussian' or filterType == 'median':
        # write the new filtered image as a NIFTI filetype to the working directory
        # to keep a copy. I'm not sure how to do this for DICOM
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName(outfile)
        writer.SetInputData(copyImage)
        writer.Write()
    
        # updates the vtk reader to the new filtered image
        smoothedImage = vtk.vtkNIFTIImageReader()
        smoothedImage.SetFileName(outfile)
        smoothedImage.Update()
    else:
        smoothedImage = filter_image
    
    return(smoothedImage)


# =============================================================================
# 
#
#
# =============================================================================
def thresholdSegment(originImage):
        
    inputImage = originImage.GetOutput()
    
    # make a copy of the input image(s) to work with and maintain original data
    binaryImage = vtk.vtkImageData()
    binaryImage.DeepCopy(inputImage) 
    
    # get the image dimensions
    imageDim = inputImage.GetDimensions()
    # imageExt = inputImage.GetExtent()
    
    # iterate through all voxels of the image set voxels to 0 or 1 value depending 
    # if they fall withing threshold values. Starting with z slice is more efficient

    for z in range(100, 110):
#    for z in range(0, imageDim[2]):
        for y in range(0, imageDim[1]):
            for x in range(0, imageDim[0]):
                
                voxelVal = inputImage.GetScalarComponentAsFloat(x, y, z, 0)
                
                if lowThresh <= voxelVal and voxelVal <= upperThresh:
                    binaryImage.SetScalarComponentFromFloat(x, y, z, 0, 1)
                else:
                    binaryImage.SetScalarComponentFromFloat(x, y, z, 0, 0)

    # update the global segmentation image as a binary image
    segmentationImage.SetInputData(binaryImage)
    segmentationImage.Update()
                                      
    return(segmentationImage)


# =============================================================================
# 
# The input should be a binary segmentation image where 1 = segmented tissue and 0 = not
#
# =============================================================================
def imageManipulation(iterations, manipulation):
    
    # used to determine the number of while loops to iterate over
    num = iterations
    
    # will dilate the image by as many pixels as specified as 'iterations'
    while num > 0:        
        inputImage = segmentationImage.GetOutput()
        
        dilationImage = vtk.vtkImageData()
        dilationImage.DeepCopy(inputImage)
        
        imageDim = inputImage.GetDimensions()
        
        # set the kernel used to determine if and where an image should be dilated
        manipulationKernel = np.array([[[0, 0, 0], [0, 1, 0], [0, 0, 0]], 
                                       [[0, 1, 0], [1, 1, 1], [0, 1, 0]], 
                                       [[0, 0, 0], [0, 1, 0], [0, 0, 0]]])
        
        # iterate through all voxels of the image
        # set voxels to 0 or 1 value depending if they meet criteria for dilation

        for z in range(100, 110):
#        for z in range(imageDim[2]):
            for y in range(imageDim[1]):
                for x in range(imageDim[0]):
                    
                    if manipulation =='dilation':
                        # if the value is 1 no need to dilate (this if statement would be 'True')
                        if inputImage.GetScalarComponentAsFloat(x, y, z, 0):
                            continue
                    elif manipulation == 'erosion':
                        # if the value is 0, no need to dilate (this if statement would be 'False')
                        if not inputImage.GetScalarComponentAsFloat(x, y, z, 0):
                            continue
                    
                    # a sub array of the image being dilated. Should be the size of the dilation kernel
                    subArray = np.empty((kernelSize, kernelSize, kernelSize), dtype=float)
                    
                    # iterate through values to append to the subArray based on 3x3x3 kernel
                    # the created sub array is composed to binary segmented image values 
                    # the kernel will be applied to the subarray to implement dilation
                    l=0 # dummy i index value
                    for i in range(max(0, (z-1)), min((z+2), imageDim[2])):
                        m=0 # dummy j index value
                        l+=1
                        for j in range(max(0, y-1), min(y+2, imageDim[1])):
                            n=0 # dummy k index value
                            m+=1
                            for k in range(max(0, x-1), min(x+2, imageDim[0])):
                                n+=1
                                voxelValue = inputImage.GetScalarComponentAsFloat(k, j, i, 0)
                                subArray[n-1][m-1][l-1] = voxelValue   
                    
                    if manipulation == 'dilation':
                        # if voxels adjacent to the current voxel are 1, dilate the image
                        binaryValue = np.multiply(manipulationKernel, subArray)
                        if np.sum(binaryValue) > 0:
                            dilationImage.SetScalarComponentFromFloat(x, y, z, 0, 1)
                    elif manipulation == 'erosion':
                        # if voxels adjacent to the current voxel are 0, erode the image
                        binaryValue = np.multiply(manipulationKernel, subArray)
                        if np.sum(binaryValue) < 7:
                            dilationImage.SetScalarComponentFromFloat(x, y, z, 0, 0)
                    
        # update the global segmented image(s) to represent the dilated segmentation            
        segmentationImage.SetInputData(dilationImage)
        segmentationImage.Update()
        num -= 1        
        
    return()

reader = readImages(imageFile)
imageSmoothed = filterSmooth(reader)
imageSegmented = thresholdSegment(imageSmoothed)

if operation == 'erosion' or operation == 'erosion':
    imageManipulation(iterations, operation)
elif operation == 'close':
    imageManipulation(iterations, 'dilation')
    imageManipulation(iterations, 'erosion')
elif operation == 'open':
    imageManipulation(iterations, 'erosion')
    imageManipulation(iterations, 'dilation')
elif operation == 'none':
    displayImages(imageSmoothed)
    
displayImages(imageSmoothed)
    