# -------------------------------------
# BMEN 619.14 / MDSC 689.03
# Advanced Medical Image Processing
# -------------------------------------
#
# Assignment #1
#	Author:	Sonny Chan
#	Date:	January 16, 2017
# -------------------------------------

import os
import sys
import vtk

# Parse command line arguments for a file
imagefile = "head.nii"
if (len(sys.argv) == 2):
	imagefile = sys.argv[1]
else:
	print('Specify input image as argument.')
	print('(using "' + imagefile + '" as default)')

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

# Get the extents of the images and report
reader.Update()
extent = reader.GetDataExtent()
print("Read image [" + imagefile + "] with extents:")
print(extent)
middle = int( (extent[4] + extent[5]) / 2 )

# Display using image viewer convenience class
viewer = vtk.vtkImageViewer()
viewer.SetInputConnection(reader.GetOutputPort())
viewer.SetZSlice(middle)

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

# Draw stuff to the screen!
viewer.Render()
iren.Start()
