# -------------------------------------
# BMEN 619.14 / MDSC 689.03
# Advanced Medical Image Processing
# -------------------------------------
#
# Assignment #2
#	Author:	Sonny Chan
#	Date:	January 23, 2017
# -------------------------------------

import os
import sys
import vtk
import math
import numpy

# Parse command line arguments for a file
imagefile = "headGaussian.nii"
if (len(sys.argv) >= 2):
	imagefile = sys.argv[1]
else:
	print ('Invoke program with: program.py <image file> [gaussian|median] [kernel size]')
	print ('(using "' + imagefile + '" as default)')

if (not os.path.exists(imagefile)):
	print( ")ERROR: " + imagefile + " does not exist!")
	sys.exit()

# Check if filter type and kernel size are specified
filterType = "gaussian"
if (len(sys.argv) >= 3):
    if (sys.argv[2].lower() == "gaussian" or sys.argv[2].lower() == "g"):
        filterType = "gaussian"
    elif (sys.argv[2].lower() == "median" or sys.argv[2].lower() == "m"):
        filterType = "median"
    else:
        print ("WARNING: filter type " + sys.argv[2] + " not recognized!")

ksize = 3
if (len(sys.argv) >= 4):
    if (sys.argv[3].isdigit()):
        ksize = int(sys.argv[3])
    else:
        print ("WARNING: could not interpret " + sys.argv[3] + " as a kernel size!")


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
		print ("ERROR: image format not recognized for " + imagefile)
		sys.exit()

# Get the read image as a vtk ImageData object
reader.Update()
imageData = reader.GetOutput()

dim = [0,0,0]
imageData.GetDimensions(dim)

dataType = imageData.GetScalarTypeAsString()
print ("Read image [" + imagefile + "] of type [" + dataType + "] with dimensions " + str(dim))

# Adjust dimension variable to filter only half the image, for visual comparison
dim[0] = int(dim[0] / 2)
middle = int(dim[2] / 2)


# Fill a numpy image array with the samples from the image
imageArray = numpy.empty( (dim[0], dim[1], dim[2]), dtype=float )
it = numpy.nditer(imageArray, flags=['multi_index'], op_flags=['writeonly'])
while not it.finished:
    index = it.multi_index;
    it[0] = imageData.GetScalarComponentAsFloat(index[0], index[1], index[2], 0)
    it.iternext()


# Specify kernel shape, then produce an index array to extract sub-images
# (koffset is half the kernel size, rounded down)
kshape = (ksize, ksize, ksize)
koffset = numpy.array([int(kshape[0]/2), int(kshape[1]/2), int(kshape[2]/2)])

ishape = (3, 1, 1, 1)
indices = numpy.indices(kshape) - koffset.reshape(ishape)

# The sub-image index array should be clamped to the following extents
limitLower = numpy.zeros(ishape, dtype=int)
limitUpper = numpy.array(dim).reshape(ishape) - 1


# Create a gaussian kernel with of the desired size by direct evaluation
sigma = 0.2 + koffset[0] * 0.4
def gaussian3D(x, y, z):
    r2 = (x-koffset[0])**2 + (y-koffset[1])**2 + (z-koffset[2])**2
    N = math.sqrt( (2.0 * math.pi * sigma ** 2) ** 3 )
    return (1.0 / N) * math.e ** (-r2 / (2.0 * sigma ** 2))

kernel = numpy.fromfunction(gaussian3D, kshape)


print ("Applying " + filterType.upper() + " filter to image with kernel size " + str(ksize))

# Iterate through the image, pulling out sub-arrays of the given kernal size
it = numpy.nditer(imageArray, flags=['multi_index'], op_flags=['writeonly'])
lastSlice = 0
while not it.finished:
    index = it.multi_index;

    # Clamp sub-image extraction indices
    kix = indices + numpy.array(index).reshape(ishape)
    numpy.clip(kix, limitLower, limitUpper, out=kix)
    
    # Extract a sub-image from the main image array
    subArray = imageArray[kix[0], kix[1], kix[2]]
    
    # Apply either gaussian or median filter
    value = subArray[koffset[0], koffset[1], koffset[2]]
    if (filterType == "gaussian"):
        value = numpy.sum(subArray * kernel)
    elif (filterType == "median"):
        value = numpy.median(subArray)

    # Write result to VTK image data
    imageData.SetScalarComponentFromFloat(index[0], index[1], index[2], 0, value)
    
    # Print a dot to indicate progress, since this loop can take a while
    if (index[0] != lastSlice):
        lastSlice = index[0]
        print ('.')
        sys.stdout.flush()
    
    it.iternext()
print ("done")


# Display using image viewer convenience class
viewer = vtk.vtkImageViewer()
viewer.SetInputData(imageData)
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
