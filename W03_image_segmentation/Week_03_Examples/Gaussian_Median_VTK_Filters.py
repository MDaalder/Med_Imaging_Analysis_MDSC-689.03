# MDSC 689.03
# Advanced Medical Image Processing
#
# Example W3.A - Demonstrating VTK filters
# Modified by Danielle Whittier
# January 31, 2020
# --------------------------------------------
#
# Assignment #2 Solution using built-in VTK filters (gaussian and median)
#
# Example command line to run the script
#
#    python Gaussian_Median_VTK_Filters.py -f median head.nii
#
# --------------------------------------------


import os
import sys
import vtk
import argparse

# Set up Argument Parser to intake the image file and choice of filter
parser = argparse.ArgumentParser (
    description="""Reads in image data and applies a filter.""")

parser.add_argument ('imagefile', default='headSaltPepper.nii')
parser.add_argument('-f', '--filter_type', choices=['gaussian', 'median', 'none'], default='gaussian',
    help="set 'gaussian' or 'median' filter type (default: %(default)s)")
args = parser.parse_args()

imagefile = args.imagefile
filterType = args.filter_type

#error argument
if (not os.path.exists(imagefile)):
	print("ERROR: " + imagefile + " does not exist!")
	sys.exit()

# Read the image data from a NIFTI file or DICOM directory
reader = vtk.vtkImageReader()

if (os.path.isdir(imagefile)):
	reader = vtk.vtkDICOMImageReader()
	reader.SetDirectoryName(imagefile)
else:
	ext = os.path.splitext(imagefile)[1]
	if (ext == ".nii" or ext == ".nifti"):
		reader = vtk.vtkNIFTIImageReader()
		reader.SetFileName(imagefile)
	else:
		print("ERROR: image format not recognized for " + imagefile)
		sys.exit()

# Get the read image as a vtk ImageData object
reader.Update()
imageData = reader.GetOutput()


# Filter the image with Gaussian or Median filter
if filterType == 'gaussian':
    filter_image = vtk.vtkImageGaussianSmooth()
    filter_image.SetInputConnection(reader.GetOutputPort())
    filter_image.SetStandardDeviation(1)
    filter_image.SetRadiusFactors(1,1,1)
    filter_image.SetDimensionality(3)
    filter_image.Update()

elif filterType == 'median':
    filter_image = vtk.vtkImageMedian3D()
    filter_image.SetInputConnection(reader.GetOutputPort())
    filter_image.SetKernelSize(3,3,3)
    filter_image.Update()

elif filterType == 'none':
    filter_image = reader

#resize the image in the x and y axis 
resize = vtk.vtkImageResize()
resize.SetInputData(filter_image.GetOutput())
resize.SetResizeMethodToMagnificationFactors()
resize.SetMagnificationFactors(2,2,0)
resize.Update()

# Set up the vtk image viewer 
viewer = vtk.vtkImageViewer()
viewer.SetInputConnection(resize.GetOutputPort())
viewer.SetZSlice(1)

# Connect an interactor to the image viewer
iren = vtk.vtkRenderWindowInteractor()
iren.SetInteractorStyle(vtk.vtkInteractorStyleImage())
viewer.SetupInteractor(iren)

# Add observers for mouse wheel events to scroll through slices
def wheelForward(obj, event):
	zSlice = viewer.GetZSlice()
	if (zSlice < viewer.GetWholeZMax()):
		viewer.SetZSlice(zSlice + 1)

def wheelBackward(obj, event):
	zSlice = viewer.GetZSlice()
	if (zSlice > viewer.GetWholeZMin()):
		viewer.SetZSlice(zSlice - 1)

iren.AddObserver("MouseWheelForwardEvent", wheelForward)
iren.AddObserver("MouseWheelBackwardEvent", wheelBackward)

# Initiate!
viewer.Render()
iren.Start()
