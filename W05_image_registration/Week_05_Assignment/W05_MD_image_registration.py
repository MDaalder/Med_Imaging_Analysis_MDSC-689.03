# -*- coding: utf-8 -*-
"""
MDSC 689.03
Assignment #5: 3D registration


inputs:
    >>>python codename.py arg_1 -f arg_2 -t arg_3 -op arg_4 -r arg_5
    
    arg_1: path to DICOM folder or NIFTI image to transform
    arg_2: type of filter to apply. Takes "gaussian" or "median" or "none"
    arg_3: global thresholding values. Must be a list of integers as "min max min2 max2".
        Use 2 pairs if you want to overlay items in marching cubes render. The second pair will be transparent.
        Use -1000 as first value to skip segmentation (to speed up ray casting!).
    arg_4: type of operation to make to the segmentation: 'dilation' 'erosion' 'none' 'close' or 'open'
        'close' will perform dilation then erosion, while 'open' will perform erosion then dilation
        Use 'none' for ray casting to speed up processing.
    arg_5: path to the .obj (or other image) to which you want to register arg_1
    
    Example:
        >>>python W05_assignment_submitted.py .../W05_registration/Week_05_Assignment/DICOM/Sawbones -f gaussian -t -900 -400 -op close -of .../W05_registration/Week_05_Assignment/SpineMesh/SawbonesSpine.obj


This code will filter and display in 3D DICOM and NIFTI medical images independent of the
Python working directory. The code will also register one source image to another target image.

Last edited on March 02 2020
# -*- coding: utf-8 -*-

@author: Matt Daalder

"""

#import packages required
import vtk   
import os
import sys
import argparse

# images to use when none given
defaultImg = '/Sawbones'

defaultObj = 'SawbonesSpine.obj'

# Use argparse to parse command line arguments
parser = argparse.ArgumentParser(
    description = """This program allows you to filter, segment, and display medical images.""")
parser.add_argument('imageFile', default = defaultImg)
parser.add_argument('-f', '--filterType', type = str, default = 'none', choices = ['none', 'gaussian', 'median'],
                    help = "Choose how to filter the image. Choices are: none, gaussian, or median. (default: %(default)s)")
parser.add_argument('-t', '--thresh', nargs='+', type = int, default = [200, 2500],
                    help = "t is the list of threshold values to use as [min, max, min2, max2]. Must be a list of len 2 or 4. (default: %(default)s)")
parser.add_argument('-op', '--operationType', type = str, default = 'none', choices = ['none', 'dilation', 'erosion', 'close', 'open'],
                    help = "Choose what operation to apply to the segmentation. Choices are: none, dilation, erosion, open, close. (default: %(default)s)")
parser.add_argument('-of', '--objFile', type = str, default = defaultObj,
                    help = "-of is the filepath to the object you want to register your source image to. (default: %(default)s)")
args = parser.parse_args()

# Argument variables to use throughout code
imageFile = args.imageFile
filterType = args.filterType
thresh = args.thresh
operation = args.operationType
objFile = args.objFile
registration = 'y'

# size of the filter and dilation/erosion kernel
# will be an input argument, maybe, in the future
kernelSize = 3

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
        elif (ext == ".obj"):
            reader = vtk.vtkOBJReader()
            reader.SetFileName(imageFile)
        else:
            print("ERROR: image format not recognized for " + imageFile)
            sys.exit()
    
    reader.Update()
            
    return (reader)


# =============================================================================
# Apply a smoothing or blurring filter to a desired image.
# Input is a vtk reader initialized medical image of type DICOM or NIFTI
# Outputs an updated vtk reader object and writes a new filtered image as NIFTI filetype
# =============================================================================
def filterSmooth(inputReader, filterIn):
    
    # Filter the image with Gaussian or Median filter
    if filterIn == 'gaussian':
        filter_image = vtk.vtkImageGaussianSmooth()
        filter_image.SetInputConnection(inputReader.GetOutputPort())
        filter_image.SetStandardDeviation(1)
        filter_image.SetRadiusFactors(1,1,1)
        filter_image.SetDimensionality(kernelSize)
        filter_image.Update()
    
    elif filterIn == 'median':
        filter_image = vtk.vtkImageMedian3D()
        filter_image.SetInputConnection(inputReader.GetOutputPort())
        filter_image.SetKernelSize(kernelSize,kernelSize,kernelSize)
        filter_image.Update()
    
    elif filterIn == 'none':
        filter_image = reader
    
    return(filter_image)

# =============================================================================
# Segments an image based on input global thershold values
# Input: a NIFTI or DICOM medical image. May or may not have already been filtered
# Output: Returns a binary image with values representing the segmented areas of the original image 
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
                                           
    return(segmentImg)

# =============================================================================
# This function erodes or dilates an existing binary segmentation image
# The inputs are a binary segmentation image and the operation itself
# the 'manipulation' can be dilation or erosion
# Returns a binary segmentation image
# =============================================================================
def imageManipulation(inputImage, manipulation):
    
    # dilate or erode the image
    dilationImg = vtk.vtkImageDilateErode3D()
    dilationImg.SetInputData(inputImage.GetOutput())
    dilationImg.SetKernelSize(kernelSize,kernelSize,kernelSize)
    if manipulation == 'dilation':
        dilationImg.SetDilateValue(1)
        dilationImg.SetErodeValue(0)
    elif manipulation == 'erosion':
        dilationImg.SetDilateValue(0)
        dilationImg.SetErodeValue(1)
    dilationImg.Update()
        
    return(dilationImg)

# =============================================================================
# Performs a marching cubes algorithm on a segmented image to visualize the image
# in 3 dimensions. 
# Input is a segmented medical image, should be gaussian filtered for best results.
# Output is a "3D" image containing only the largest volume of connected voxels
# within the segmentation range.
# =============================================================================
def marchingCubes(inputImage):
    
    # initialise 3D marching cubes render
    marchingCubes = vtk.vtkMarchingCubes()
    marchingCubes.SetInputConnection(inputImage.GetOutputPort())
    marchingCubes.ComputeNormalsOn()
    marchingCubes.SetValue(0, 1.0)

    # get largest object only (remove noise or unwanted objects)
    largestObject = vtk.vtkPolyDataConnectivityFilter()
    largestObject.SetInputConnection(marchingCubes.GetOutputPort())
    largestObject.SetExtractionModeToLargestRegion()
    largestObject.ColorRegionsOn()
    largestObject.Update()
    
    # smooth the image
    smoothedObject = vtk.vtkSmoothPolyDataFilter()
    smoothedObject.SetInputConnection(marchingCubes.GetOutputPort())
    smoothedObject.SetNumberOfIterations(5)
    smoothedObject.SetRelaxationFactor(0.3)
    smoothedObject.FeatureEdgeSmoothingOff()
    smoothedObject.BoundarySmoothingOn()
    smoothedObject.Update()
    
    # update normals on the smoothed image
    finalObject = vtk.vtkPolyDataNormals()
    finalObject.SetInputConnection(smoothedObject.GetOutputPort())
    finalObject.ComputePointNormalsOn()
    finalObject.ComputeCellNormalsOn()
    finalObject.Update()

    return(finalObject)

# =============================================================================
# Takes the output from the marching cubes algorithm and displays the 3D image
# Input: either one or two vtk marching cubes images. The 2nd image will be displayed
# with transparency on. Requires that two threshold pairs are given when initialising the program.
# Output returns nothing except a visualization.
#
# Can easily define tissue colours in the given dictionary
# Need to smooth the image, it's very blocky. Done here or in def marchingCubes()????
# =============================================================================
def display3DImagesCubes(reader, readerTrans):
    
    # create a dict of preset colors (i.e. bone, skin, blood, etc)
    colors = {}
    colors = {'skin':(0.90, 0.76, 0.6), 
              'bone':(0.83, 0.8, 0.81), 
              'blood':(0.65, 0.1, 0.1), 
              'green':(0, 0.9, 0.2), 
              'purple':(0.7, 0.61, 0.85)}

    # initialise mapper of opaque 3D image
    mapper3DOpaque = vtk.vtkPolyDataMapper()
    mapper3DOpaque.SetInputConnection(reader.GetOutputPort())
    mapper3DOpaque.ScalarVisibilityOff()

    # initialise the opaque actor
    actor3DOpaque = vtk.vtkActor()
    actor3DOpaque.SetMapper(mapper3DOpaque)
    actor3DOpaque.GetProperty().SetOpacity(1.0)
    actor3DOpaque.GetProperty().SetColor(colors['bone'])

    if readerTrans:
        # initialise the 3D mapper to be transparent
        mapper3DTrans = vtk.vtkPolyDataMapper()
        mapper3DTrans.SetInputConnection(readerTrans.GetOutputPort())
        mapper3DTrans.ScalarVisibilityOff()

        # initialise the transparent actor
        actor3DTrans = vtk.vtkActor()
        actor3DTrans.SetMapper(mapper3DTrans)
        actor3DTrans.GetProperty().SetOpacity(0.8)
        actor3DTrans.GetProperty().SetColor(colors['blood'])


    # create the renderer and add actors
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor3DOpaque)
    if readerTrans:
        renderer.AddActor(actor3DTrans)
    
    # create the render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1000, 1000)
    
    # Connect an interactor to the image viewer
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    
    # initialise the interactor
    interactor.Initialize()
    
    # render the scene with all actors in it
    renderWindow.Render()
    
    # Start the event loop for the interactor
    interactor.Start()
    
    return()

# =============================================================================
# Takes a medical image and displays it in "3D" using ray casting technique
# Input: a vtk initialised nifti or dicom medical image, ideally with a gaussian filter applied
# Output returns nothing, but displays an image.
# Can easily define tissue intensity ranges and colours in the given colorTable dictionary
# =============================================================================
def display3DImagesRay(reader):
    
    # create a colour lookup table for different tissue types based on voxel intensity
    # the convention is tissue[(low HU, R, G, B), (hi HU, R, G, B)]
    colorTable = {}
    colorTable = {'background':[(-4000, 0.0, 0.0, 0.0),(-600, 0.0, 0.0, 0.0)], 
                'skin':[(-500, 0.90, 0.76, 0.6),(-100, 0.90, 0.76, 0.6)], 
                'organs':[(100, 0.65, 0.1, 0.1),(170, 0.65, 0.1, 0.1)],
                'bone':[(250, 0.83, 0.8, 0.81),(2300, 0.83, 0.8, 0.81)]} 

    # apply a median filter to remove speckling
    filterMedian = filterSmooth(reader, 'median')

    # initialise the raycast mapper
    rayMapper = vtk.vtkGPUVolumeRayCastMapper()
    rayMapper.SetInputConnection(filterMedian.GetOutputPort())
    
    # map voxel intensities (tissue types) to colours
    itemColor = vtk.vtkColorTransferFunction()
    itemColor.AddRGBPoint(*(colorTable['background'][0]))
    itemColor.AddRGBPoint(*(colorTable['background'][1]))
    itemColor.AddRGBPoint(*(colorTable['skin'][0]))
    itemColor.AddRGBPoint(*(colorTable['skin'][1]))
    itemColor.AddRGBPoint(*(colorTable['organs'][0]))
    itemColor.AddRGBPoint(*(colorTable['organs'][1]))
    itemColor.AddRGBPoint(*(colorTable['bone'][0]))
    itemColor.AddRGBPoint(*(colorTable['bone'][1]))
    
    # set opacity of different voxel intensities (tissues types)
    itemScalarOpacity = vtk.vtkPiecewiseFunction()
    itemScalarOpacity.AddPoint(float(colorTable['background'][0][0]), 0.0)
    itemScalarOpacity.AddPoint(float(colorTable['background'][1][0]), 0.0)
    itemScalarOpacity.AddPoint(float(colorTable['skin'][0][0]), 0.0)
    itemScalarOpacity.AddPoint(float(colorTable['skin'][1][0]), 0.0)
    itemScalarOpacity.AddPoint(float(colorTable['organs'][0][0]), 0.6)
    itemScalarOpacity.AddPoint(float(colorTable['organs'][1][0]), 0.2)
    itemScalarOpacity.AddPoint(float(colorTable['bone'][0][0]), 1.0)
    itemScalarOpacity.AddPoint(float(colorTable['bone'][1][0]), 1.0)
    
    # Gradient function to control opacity at boundaries between tissue types
    itemGradientOpacity = vtk.vtkPiecewiseFunction()
    itemGradientOpacity.AddPoint(0, 0.0)
    itemGradientOpacity.AddPoint(90, 0.5)
    itemGradientOpacity.AddPoint(100, 1.0)
    
    # set properties of the items to be rendered
    itemProperty = vtk.vtkVolumeProperty()
    itemProperty.SetColor(itemColor)
    itemProperty.SetScalarOpacity(itemScalarOpacity)
    itemProperty.SetGradientOpacity(itemGradientOpacity) 
    itemProperty.SetInterpolationTypeToLinear()
    itemProperty.ShadeOn()
    
    # initialise the volume to be rendered
    rayActor = vtk.vtkVolume()
    rayActor.SetMapper(rayMapper)
    rayActor.SetProperty(itemProperty)
    
    # create the renderer and add volume
    renderer = vtk.vtkRenderer()
    renderer.AddViewProp(rayActor)
    renderer.ResetCamera()

    # create the render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1000, 1000)
    
    # Connect an interactor to the image viewer
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    
    # initialise the interactor
    interactor.Initialize()
    
    # render the scene with all actors in it
    renderWindow.Render()
    
    # Start the event loop for the interactor
    interactor.Start()
    return()


# =============================================================================
# This code will register two image by finding the transform required to do so,
# then apply the transform to the original image dataset
# objImage is the image to register to (target)
# sourceImage is the image you want to transform to match the coordinates of objImage
#   it should be a 3D surface image, likely from marching cubes algorithm
# =============================================================================
def registerImage(objImage, sourceImage):
    
    # use iteratice closest points (ICP) to get the registration transform
    closestPoints = vtk.vtkIterativeClosestPointTransform()
    closestPoints.SetTarget(objImage.GetOutput())
    closestPoints.SetSource(sourceImage.GetOutput())
    closestPoints.GetLandmarkTransform().SetModeToRigidBody()
    closestPoints.SetMaximumNumberOfIterations(600)
    # closestPoints.StartByMatchingCentroidsOn()
    closestPoints.SetMaximumMeanDistance(.001)
    closestPoints.CheckMeanDistanceOn()
    closestPoints.DebugOn()
    closestPoints.Modified()
    closestPoints.Update()
    
    # apply the transformation to the original source medical image
    sourceTransformed = vtk.vtkImageReslice()
    sourceTransformed.SetInputConnection(sourceImage.GetOutputPort())
    sourceTransformed.SetResliceTransform(closestPoints)
    sourceTransformed.SetBackgroundLevel(-1500)
    sourceTransformed.Update()
    
    # apply the transformation to the 3D marching cubes image
    cubesTransformed = vtk.vtkTransformPolyDataFilter()
    cubesTransformed.SetInputConnection(sourceImage.GetOutputPort())
    cubesTransformed.SetTransform(closestPoints)
    cubesTransformed.Update()
    
    return(cubesTransformed)

# =============================================================================
#  used to display the target image in white and the source transformed image
#  in purple to check registration.
#  Inputs:
#  objImage is the target image
#  sourceImage is a 3D rendered surface image, likely from marching cubes
# =============================================================================
def displayRegisteredImages(objImage, sourceImage):
    
    # original images before registration
    
    # mapper of the transformed image    
    mapperTransformedSource = vtk.vtkPolyDataMapper()
    mapperTransformedSource.SetInputConnection(sourceImage.GetOutputPort())
    mapperTransformedSource.ScalarVisibilityOff()
    
    # mapper of the target .obj image
    mapperObjImage = vtk.vtkPolyDataMapper()
    mapperObjImage.SetInputConnection(objImage.GetOutputPort())
    
    # transformed actor
    actorTransformedSource = vtk.vtkActor()
    actorTransformedSource.SetMapper(mapperTransformedSource)
    actorTransformedSource.GetProperty().SetColor(0.83, 0.8, 0.81) #purple
    
    # .obj actor
    actorObjImage = vtk.vtkActor()
    actorObjImage.SetMapper(mapperObjImage)
    actorObjImage.GetProperty().SetColor(0.7, 0.61, 0.85) # white
    
    # create the renderer for the transformed image and add actors
    rendererRegistered = vtk.vtkRenderer()
    rendererRegistered.AddActor(actorTransformedSource)
    rendererRegistered.AddActor(actorObjImage)

    # create the render window
    renderWindowRegistered = vtk.vtkRenderWindow()
    renderWindowRegistered.AddRenderer(rendererRegistered)
    renderWindowRegistered.SetSize(1000, 1000)
    
    # Connect an interactor to the image viewer
    interactorRegistered = vtk.vtkRenderWindowInteractor()
    interactorRegistered.SetRenderWindow(renderWindowRegistered)
    interactorRegistered.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    
    # initialise the interactor
    interactorRegistered.Initialize()
    
    # render the scene with all actors in it
    renderWindowRegistered.Render()
    
    # Start the event loop for the interactor
    interactorRegistered.Start()
    
    
    return()

# =============================================================================
# The code that runs all of the functions above to read, filter, display an image
# =============================================================================

# read in the image files(s)
reader = readImages(imageFile)

# apply a filter to the image (or not)
if not filterType == 'none':
    imageSmoothed = filterSmooth(reader, filterType)
else:
    imageSmoothed = reader


# segment the image based on global threshold values
if not thresh[0] == -1000: # if the threshold value is -1000, we don't run thresholding
    lowThresh = thresh[0]
    upperThresh = thresh[1]
    segmentImg = thresholdSegment(imageSmoothed)
    if len(thresh) == 4:
        lowThresh = thresh[2]
        upperThresh = thresh[3]
        segmentImgTrans = thresholdSegment(readImages(objFile))
    else:
        segmentImgTrans = False
else:
    segmentImg = imageSmoothed
    segmentImgTrans = False
    pass


# determine what operations to run on the segmented image
if operation == 'none':
    pass
elif operation == 'dilation' or operation == 'erosion':
    segmentImg = imageManipulation(segmentImg, operation)
    if segmentImgTrans:
        segmentImgTrans = imageManipulation(segmentImgTrans, operation)
elif operation == 'close':
    segmentImg = imageManipulation(segmentImg, 'dilation')
    segmentImg = imageManipulation(segmentImg, 'erosion')
    if segmentImgTrans:
           segmentImgTrans = imageManipulation(segmentImgTrans, 'dilation')
           segmentImgTrans = imageManipulation(segmentImgTrans, 'erosion')
elif operation == 'open':
    segmentImg = imageManipulation(segmentImg, 'erosion')
    segmentImg = imageManipulation(segmentImg, 'dilation')
    if segmentImgTrans:
        segmentImgTrans = imageManipulation(segmentImgTrans, 'erosion')
        segmentImgTrans = imageManipulation(segmentImgTrans, 'dilation')
    
# register and display the image
if registration == 'y' or registration == 'Y':
    cubes3D = marchingCubes(segmentImg)
    objectFile = readImages(objFile)
    
    transformed3D = registerImage(objectFile, cubes3D)
    displayRegisteredImages(objectFile, transformed3D)