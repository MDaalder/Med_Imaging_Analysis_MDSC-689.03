#!/usr/bin/env python3

"""
MDSC 689.03
Assignment #3: Segmentation and Dilation/Erosion

inputs:
    >>>python codename.py arg_1 -f arg_2 -lt arg_3 -ut arg_4 -op arg_5 -it arg_6
    
    arg_1: path to DICOM folder or NIFTI image
    arg_2: type of filter to apply. Takes "gaussian" or "median" or "none"
    arg_3: minimum global thresholding value. Must be an integer. Use -1000 to skip segmentation.
    arg_4: maximum global thresholding value. Must be an integer.
    arg_5: type of operation to make to the segmentation: 'dilation' 'erosion' 'none' 'close' or 'open'
        'close' will perform dilation then erosion, while 'open' will perform erosion then dilation
    arg_6: how many iterations of the operation to implement. Must be an integer.
    
    Example:
        >>>python W04_assignment.py C:/Users/mattd/Documents/GitHub/MDSC-689.03/W01_vtk_intro/W01_Assignment/NIFTI/head.nii -f none -lt -1000 -ut 100 -op none -it 0
        
This code will filter and display a single set of DICOM or NIFTI medical images
independent of the Python working directory with a segmentation over top of it.
Dilation and/or erosion can be applied to the segmentation. The code will also 
write a new filtered image as NIFTI file type to the working directory so you 
can access it in the future.

Last edited on Feb 09 2020
# -*- coding: utf-8 -*-

@author: MattD

"""

#import packages required
import vtk   
import os
import sys
import argparse

# image to use when none given
defaultImg = 'C:/Users/mattd/Documents/GitHub/MDSC-689.03/W01_vtk_intro/W01_Assignment/NIFTI/head.nii'

# Use argparse to parse command line arguments
parser = argparse.ArgumentParser(
    description = """This program allows you to filter, segment, and display medical images.""")
parser.add_argument('imageFile', default = defaultImg)
parser.add_argument('-f', '--filterType', type = str, default = 'none', choices = ['none', 'gaussian', 'median'],
                    help = "Choose how to filter the image. Choices are: none, gaussian, or median. (default: %(default)s)")
parser.add_argument('-lt', '--lowThresh', type = int, default = 200,
                    help = "lt is the lower threshold. (default: %(default)s)")
parser.add_argument('-ut', '--upperThresh', type = int, default = 1000,
                    help = "ut is the upper threshold. (default: %(default)s)")
parser.add_argument('-op', '--operationType', type = str, default = 'none', choices = ['none', 'dilation', 'erosion', 'close', 'open'],
                    help = "Choose what operation to apply to the segmentation. Choices are: none, dilation, erosion, open, close. (default: %(default)s)")
parser.add_argument('-it', '--iterations', type = float, default = 1,
                    help = "-it is the number of iterations to perform of the applied operation. (default: %(default)s)")
args = parser.parse_args()

# Argument variables to use throughout code
imageFile = args.imageFile
filterType = args.filterType
lowThresh = args.lowThresh
upperThresh = args.upperThresh
operation = args.operationType
iterations = args.iterations

# size of the filter and dilation/erosion kernel
# will be an input argument, maybe, in the future
kernelSize = 3

# display properties for the vtk window
colorWindow = 1000
colorLevel = 200

# implement the segmentation image object to be updated as the code runs
segmentationImage = vtk.vtkPassThroughFilter()
  
# =============================================================================
# Reads a medical image (DICOM or NIFTI).
# Returns a vtk reader object.
# Checks to see if the file or directory is useable.
# This allows the location of the file(s) used to be independent of the working directory
# =============================================================================
def readImages(imageFile):

    # define the variables to determine the location of DICOM directory or NIFTI file

    if os.path.isdir(imageFile):
        print("Using " + os.path.basename(imageFile) + ' as directory to read from')
    elif os.path.exists(imageFile):
        print("Using " + os.path.splitext(imageFile)[0] + ' as image to read')
    else:
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
            
    return (reader)

# =============================================================================
# Display everything in vtk window.
# Includes information about image slice, image windowing, and segmentation thresholds.
#
# Input: an intialised vtkImageReader object. Also reads a global segmentation image.
#
# 
# Eventual wants: display patient id, patient position, and automatic center positioning of medical images 
# =============================================================================
def display2DImages(reader): 
    
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
    # mapToColors.SetInputConnection(dilationImg.GetOutputPort())
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
    if not lowThresh == -1000:
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

def display3DImagesCubes(reader, readerTrans):
    
    # create a dict of preset colors (i.e. bone, skin, blood, etc)
    colors = {}
    colors = {'bone':[], 'skin':[], 'blood':[], 'green':[], 'purple':[]}

    # initialise mapper of opaque 3D image
    mapper3DOpaque = vtk.vtkPolyDataMapper()
    mapper3DOpaque.SetInputConnection(reader.GetOutputPort())
    mapper3DOpaque.ScalarVisibilityOff()

    # initialise the opaque actor
    actor3DOpaque = vtk.vtkActor()
    actor3DOpaque.SetMapper(mapper3DOpaque)
    actor3DOpaque.GetProperty().SetOpacity(1.0)
    actor3DOpaque.GetProperty().SetColor() asdf

    if readerTrans == True:
        # initialise the 3D mapper to be transparent
        mapper3DTrans = vtk.vtkPolyDataMapper()
        mapper3DTrans.SetInputConnection(readerTrans,GetOutputPort())
        mapper3DTrans.ScalarVisibilityOff()

        # initialise the transparent actor
        actor3DTrans = vtk.vtkActor()
        actor3DTrans = SetMapper(mapper3DTrans)
        actor3DTrans = GetProperty().SetOpacity(0.5)
        actor3DTrans = GetProperty().SetColor() asdf


    # create the renderer and add actors
    renderer = vtk.vtkRenderer()
    render.AddActor(actor3DOpaque)
    if readerTrans == True:
        render.AddActor(actor3DTrans)
    
    # create the render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1000, 1000)
    
    # Connect an interactor to the image viewer
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())
    
    # initialise the interactor
    interactor.Initialize()
    
    # render the scene with all actors in it
    renderWindow.Render()
    
    # Start the event loop for the interactor
    interactor.Start()
    
    return()

def display3DImagesRay(reader):

    return()
    
# =============================================================================
# Apply a smoothing or blurring filter to a desired image.
# Input is a vtk reader initialized medical image of type DICOM or NIFTI
# Outputs an updated vtk reader object and writes a new filtered image as NIFTI filetype
# =============================================================================
def filterSmooth(inputReader):
    
    # Filter the image with Gaussian or Median filter
    if filterType == 'gaussian':
        filter_image = vtk.vtkImageGaussianSmooth()
        filter_image.SetInputConnection(inputReader.GetOutputPort())
        filter_image.SetStandardDeviation(1)
        filter_image.SetRadiusFactors(1,1,1)
        filter_image.SetDimensionality(kernelSize)
        filter_image.Update()
    
    elif filterType == 'median':
        filter_image = vtk.vtkImageMedian3D()
        filter_image.SetInputConnection(inputReader.GetOutputPort())
        filter_image.SetKernelSize(kernelSize,kernelSize,kernelSize)
        filter_image.Update()
    
    elif filterType == 'none':
        filter_image = reader
    
    return(filter_image)

# =============================================================================
# Segments an image based on input global thershold values
# Input: a NIFTI or DICOM medical image. May or may not have already been filtered
# Output: Returns nothing, but updates a global segmentation image with binary 
# values representing the segmented areas of the original image 
# 1 = segmented tissue, 0 = not segmented
# =============================================================================
def thresholdSegment(originImage):
    
    # message("Segmenting the image between threshold values of %d and %d..." % (lowThresh, upperThresh))    
    
    # sets the image we want to work with
    inputImage = originImage.GetOutput()
    
    # Threshold the image and segment
    segmentImg = vtk.vtkImageThreshold()
    segmentImg.SetInputData(inputImage)
    segmentImg.ThresholdBetween(lowThresh, upperThresh)
    segmentImg.ReplaceInOn()
    segmentImg.SetInValue(1)
    segmentImg.ReplaceOutOn()
    segmentImg.SetOutValue(0)
    segmentImg.SetOutputScalarTypeToFloat()
    segmentImg.Update()
    
    # update the global segmentation image as a segmented binary image
    segmentationImage.SetInputConnection(segmentImg.GetOutputPort())
    segmentationImage.Update()
                                          
    return()

# =============================================================================
# This function erodes or dilates an existing binary segmentation image
# The inputs are the number of times to run the operation and the operation itself
# the 'manipulation' can be dilation or erosion, iterations an integer
# Returns nothing, but updates the global binary segmentation image
# =============================================================================
def imageManipulation(iterations, manipulation):
    
    # used to determine the number of while loops to iterate over
    num = iterations
    
    while num >0:
        
        # dilate or erode the image
        dilationImg = vtk.vtkImageDilateErode3D()
        dilationImg.SetInputData(segmentationImage.GetOutput())
        dilationImg.SetKernelSize(kernelSize,kernelSize,kernelSize)
        if manipulation == 'dilation':
            dilationImg.SetDilateValue(1)
            dilationImg.SetErodeValue(0)
        elif manipulation == 'erosion':
            dilationImg.SetDilateValue(0)
            dilationImg.SetErodeValue(1)
        dilationImg.Update()
        
        # update the global segmented image(s) to represent the dilated segmentation  
        segmentationImage.SetInputConnection(dilationImg.GetOutputPort())
        segmentationImage.Update()
        num -= 1
        
    return()

def marchingCubes():
    
    # initialise 3D marching cubes render
    marchingCubes = vtk.vtkMarchingCubes()
    marchingCubes.SetInputConnection(segmentationImage.GetOutputPort())
    marchingCubes.ComputeNormalsOn()
    marchingCubes.SetValue(0, 1.0)

    # get largest object only (remove noise or unwanted objects)
    largestObject = vtk.vtkPolyDataConnectivityFilter()
    largestObject.SetInputConnection(marchingCubes.GetOutputPort())
    largestObject.SetExtractionModeToLargestRegion()
    largestObject.ColorRegionsOn()
    largestObject.Update()

    return(largestObject)


# read in the image files(s)
reader = readImages(imageFile)

# apply a filter to the image (or not). Should change the code so it doesn't run through this
# if 'none' is input when running the program. Not a priority right now.
if not filterType == 'none':
    imageSmoothed = filterSmooth(reader)
else:
    imageSmoothed = reader

# segment the image based on global threshold values
if not lowThresh == -1000:
    thresholdSegment(imageSmoothed)
else:
    pass

# determine what operations to run on the segmented image
if operation == 'none':
    pass
elif operation == 'dilation' or operation == 'erosion':
    imageManipulation(iterations, operation)
elif operation == 'close':
    imageManipulation(iterations, 'dilation')
    imageManipulation(iterations, 'erosion')
elif operation == 'open':
    imageManipulation(iterations, 'erosion')
    imageManipulation(iterations, 'dilation')

# display 2D images and segmentation
display2DImages(imageSmoothed)
    