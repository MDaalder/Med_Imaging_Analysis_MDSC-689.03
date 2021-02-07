# -------------------------------------
# BMEN 619.14 / MDSC 689.03
# Advanced Medical Image Processing
# -------------------------------------
#
# Assignment #3
#	Author:	Sonny Chan, Steven Boyd
#	Date:	January 30, 2017
# -------------------------------------
#
# Execution: python assign3-sc.py head.nii -k 5 -t -400 40 150 2000
#
# This script applied a global threshold to an input image. There is an option to then dilate the image
# using a kernel size specified by the user. 


import os
import sys
import vtk
import numpy
import argparse
from vtk.util import numpy_support


# Use argparse to parse command line arguments
parser = argparse.ArgumentParser(
    description="""Apply a global threshold to an image, and optionally a dilation filter.""")

parser.add_argument('imagefile', default='head.nii')
parser.add_argument('-k', '--kernel_size', type=int, default=3, choices=[1,3,5,7],
    help="set the kernel size of the filter, 1 for no dilation (default: %(default)s)")
parser.add_argument('-t', '--thresholds', nargs='+', type=int, default=[-400, 40, 150, 2000],
    help="set threshold intervals with value pairs, L1 H1 L2 H2 ... (default: %(default)s)")
args = parser.parse_args()

imagefile = args.imagefile      # input file
ksize = args.kernel_size        # dilation kernel size
tlist = sorted(args.thresholds) # sorted threshold interval values

if len(tlist) % 2 != 0:
    print("ERROR: List of specified threshold values must be even length (low, high pairs)!")
    sys.exit()

# Defined segmentation overlay colours (up to six)
colours = [ [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1] ]


# Read the image data from a NIFTI file or DICOM directory
if (not os.path.exists(imagefile)):
    print("ERROR: " + imagefile + " does not exist!")
    sys.exit()

reader = vtk.vtkImageReader()

if os.path.isdir(imagefile):
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
dim = imageData.GetDimensions()

dataType = imageData.GetScalarTypeAsString()
print("Read image [" + imagefile + "] of type [" + dataType + "] with dimensions " + str(dim))

# Reverse the dimensions tuple for z-y-x indexing, and get the middle slice index
ldim = list(dim)
ldim.reverse()
dim = tuple(ldim)
middle = int(dim[0] / 2)


# Convert the vtkImageData to a NumPy array for processing
imageDataArray = imageData.GetPointData().GetAbstractArray(0)
imageArray = numpy_support.vtk_to_numpy(imageDataArray)
imageArray.resize(dim)


# Make sure specified thresholds fall within input range
inputRange = imageDataArray.GetRange()
tlist = numpy.clip(tlist, inputRange[0], inputRange[1]).tolist()

# Use interpolate function to do thresholding here
thresholds = list(zip(*[iter(tlist)]*2))
print("Segmenting input image with threshold ranges " + str(thresholds))

tlist = [inputRange[0]] + tlist + [inputRange[1]]
xp = []
fp = []
for i in range(0, len(tlist) - 1):
    xp += tlist[i : i+2]
    fp += [0, 0] if i%2 == 0 else [(i+1)/2] * 2

segmented = numpy.interp(imageArray, xp, fp).astype('u1')


# Specify dilation kernel shape, then produce an index array to extract sub-images
# (koffset is half the kernel size, rounded down)
kshape = (ksize, ksize, ksize)
koffset = numpy.array([int(kshape[0]/2), int(kshape[1]/2), int(kshape[2]/2)])

ishape = (3, 1, 1, 1)
indices = numpy.indices(kshape) - koffset.reshape(ishape)

# The sub-image index array should be clamped to the following extents
limitLower = numpy.zeros(ishape, dtype=int)
limitUpper = numpy.array(dim).reshape(ishape) - 1


# Create a dilation kernel with of the desired size, which has 1's set on entries
# within a ksize/2 radius of the centre
def dilation3D(x, y, z):
    r2 = (x-koffset[0])**2 + (y-koffset[1])**2 + (z-koffset[2])**2
    return numpy.clip(numpy.sign((koffset[0])**2 - r2) + 1, 0, 1)

kernel = numpy.fromfunction(dilation3D, kshape).astype('u1')
#print kernel


# Apply the kernel to dilate the image
print("Applying dilation to segmented image with kernel size " + str(ksize))

# Iterate through the image, pulling out sub-arrays of the given kernal size
dilated = numpy.copy(segmented)
if ksize > 1:
    it = numpy.nditer(dilated, flags=['multi_index'], op_flags=['writeonly'])
    lastSlice = 0
    while not it.finished:
        index = it.multi_index;
        
        # Clamp sub-image extraction indices
        kix = indices + numpy.array(index).reshape(ishape)
        numpy.clip(kix, limitLower, limitUpper, out=kix)
        
        # Extract a sub-image from the main image array
        subArray = segmented[kix[0], kix[1], kix[2]]
        
        # Apply the dilation filter
        it[0] = numpy.amax(subArray * kernel)

        # Print a dot to indicate progress, since this loop can take a while
        if (index[0] != lastSlice):
            lastSlice = index[0]
            print('.', end=' ')
            sys.stdout.flush()

        it.iternext()
print("done")


# Write the processed image data back to the vtkImageData object
processedDataArray = numpy_support.numpy_to_vtk(dilated.ravel())

segmentation = vtk.vtkImageData()
segmentation.CopyStructure(imageData)
segmentation.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
segmentationDataArray = segmentation.GetPointData().GetAbstractArray(0)
segmentationDataArray.DeepCopy(processedDataArray)

# Create lookup table for the segmentation
lut = vtk.vtkLookupTable()
lut.SetTableRange([0, len(thresholds)])
lut.SetNumberOfTableValues(len(thresholds) + 1)
lut.SetTableValue(0, 0, 0, 0, 0)
lut.SetTableValue(1, colours[1][0], colours[1][1], colours[1][2], 0.4)
for i in range(1, len(thresholds) + 1):
    lut.SetTableValue(i, colours[i][0], colours[i][1], colours[i][2], 0.4)
lut.SetAboveRangeColor(0, 0, 0, 0)
lut.Build()

# Map the segmentation through the lookup table
colourMapper = vtk.vtkImageMapToColors()
colourMapper.SetLookupTable(lut)
colourMapper.PassAlphaToOutputOn()
colourMapper.SetInputData(segmentation)
colourMapper.Update()


# Display using image viewer convenience class
viewer = vtk.vtkImageViewer2()
viewer.SetInputData(imageData)
viewer.SetSlice(middle)

# Connect an interactor to the image viewer
iren = vtk.vtkRenderWindowInteractor()
viewer.SetupInteractor(iren)
viewer.GetInteractorStyle().SetInteractionModeToImageSlicing()

# Create an actor for the segmented image overlay and add to viewer
segmentation = colourMapper.GetOutput()
segmentationActor = vtk.vtkImageActor()
segmentationActor.GetMapper().SetInputData(segmentation)
extent = list(segmentation.GetExtent())
extent[4] = extent[5] = middle
segmentationActor.SetDisplayExtent(extent)
viewer.GetRenderer().AddActor(segmentationActor)

# Create event handlers for mouse wheel events to scroll through slices
def wheelForward(obj, event):
    currentSlice = viewer.GetSlice()
    if currentSlice < viewer.GetSliceMax():
        extent[4] = extent[5] = currentSlice + 1
        segmentationActor.SetDisplayExtent(extent)
        viewer.SetSlice(currentSlice + 1)

def wheelBackward(obj, event):
    currentSlice = viewer.GetSlice()
    if currentSlice > viewer.GetSliceMin():
        extent[4] = extent[5] = currentSlice - 1
        segmentationActor.SetDisplayExtent(extent)
        viewer.SetSlice(currentSlice - 1)

# Replace the event handler observers for the mouse wheel in the interactor
iren.RemoveObservers("MouseWheelForwardEvent")
iren.RemoveObservers("MouseWheelBackwardEvent")
iren.AddObserver("MouseWheelForwardEvent", wheelForward)
iren.AddObserver("MouseWheelBackwardEvent", wheelBackward)

# Draw stuff to the screen!
viewer.Render()
iren.Initialize()
iren.Start()
