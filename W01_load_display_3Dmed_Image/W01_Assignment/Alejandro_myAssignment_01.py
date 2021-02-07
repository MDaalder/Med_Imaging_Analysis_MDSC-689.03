# MDSC 689.03
# Advanced Medical Image Processing
#
# Assignment 01 - Load and Display a 3D medical image
# Alejandro_Gutierrez
# January 27, 2020
# ----------------------------------------------------------------------------------------
#
# This program loads and displays a medical image, either NIfTI or DICOM.
# The images are scanned by default from the same folder the python script is executed.
# Additionally it allows for keyboard controls over slice, window and level.
#
# Example command lines to run the script
#
#    python myAssignment_01.py
#    python myAssignment_01.py /home/User/myFolder/
#
# -----------------------------------------------------------------------------------------

# Import libraries.
import vtk
import os
import sys


# Setup text mapper and pass text properties to it.
textMapper = vtk.vtkTextMapper()
textProperties = vtk.vtkTextProperty()
textProperties.SetFontFamilyToCourier()
textProperties.SetFontSize(20)
textProperties.SetVerticalJustificationToBottom()
textProperties.SetJustificationToLeft()
textMapper.SetTextProperty(textProperties)

# Setup another text mapper and pass text properties to it.
textMapperB = vtk.vtkTextMapper()
textPropertiesB = vtk.vtkTextProperty()
textPropertiesB.SetFontFamilyToCourier()
textPropertiesB.SetFontSize(20)
textPropertiesB.SetVerticalJustificationToBottom()
textPropertiesB.SetJustificationToRight()
textMapperB.SetTextProperty(textPropertiesB)

# Initialize color range variable with a default of 3000.
colorRange = 3000

# ----------------------------------------------------------
#   Define set_message() function.
#   Updates the text actors in the rendered window.
# ----------------------------------------------------------

def set_message():

    # Display the current slice.
    msg = "Slice {} of {}\nUp and Down arrows to browse.".format(imageViewer.GetSlice() + 1,
                                                                 imageViewer.GetSliceMax() + 1)
    textMapper.SetInput(msg)
    textActor = vtk.vtkActor2D()
    textActor.SetMapper(textMapper)
    textActor.SetPosition(20, 20)
    imageViewer.GetRenderer().AddActor2D(textActor)

    # Create a visual representation of the current window and level by printing dashes and brackets.
    # Example: ----------[-------]---------
    visual = ""
    openBracket = False
    closingBracket = False
    for n in range(20):
        if ((n * (colorRange/20)) - 1500) >= (imageViewer.GetColorLevel() - (imageViewer.GetColorWindow()/2)) \
                and not openBracket:
            visual = visual + "["
            openBracket = True
        elif ((n * (colorRange/20)) - 1500) >= (imageViewer.GetColorLevel() + (imageViewer.GetColorWindow()/2)) \
                and not closingBracket:
            visual = visual + "]"
            closingBracket = True
        visual = visual + "-"

    # Display current window and level values, together with the previously computed visual.
    msgB = ("Window: {} Level: {}\n" + visual + "\nLeft and Right (Level)\nPlus and Minus (Window)").format(
        round(imageViewer.GetColorWindow()), round(imageViewer.GetColorLevel()))
    textMapperB.SetInput(msgB)
    textActorB = vtk.vtkActor2D()
    textActorB.SetMapper(textMapperB)
    textActorB.SetPosition(980, 20)
    imageViewer.GetRenderer().AddActor2D(textActorB)


# ----------------------------------------------------------------------------------------------
#   Define change_slice() function.
#   This function is called when keyboard keys are pressed, some keys will be assigned a task.
# ----------------------------------------------------------------------------------------------

def change_slice(obj, ev):

    # Get the pressed key.
    key = obj.GetKeySym()

    # Identify the pressed key and perform a task.
    if key == "Up" and imageViewer.GetSlice() < imageViewer.GetSliceMax():
        imageViewer.SetSlice(imageViewer.GetSlice() + 1)  # Go to next slice.
    elif key == "Down" and imageViewer.GetSlice() > imageViewer.GetSliceMin():
        imageViewer.SetSlice(imageViewer.GetSlice() - 1)  # Go to previous slice.
    elif key == "Left":
        imageViewer.SetColorLevel(imageViewer.GetColorLevel() - (colorRange/250))  # Decrease level value.
    elif key == "Right":
        imageViewer.SetColorLevel(imageViewer.GetColorLevel() + (colorRange/250))  # Increase level value.
    elif key == "KP_Add" or key == "plus":
        imageViewer.SetColorWindow(imageViewer.GetColorWindow() + (colorRange/250))  # Increase window value.
    elif key == "KP_Subtract" or key == "minus":
        imageViewer.SetColorWindow(imageViewer.GetColorWindow() - (colorRange/250))  # Decrease window value.

    #  Call set_message() to update texts with new values.
    set_message()
    imageViewer.Render()


# Scan files in current folder or in assigned one if argument is present.
if len(sys.argv) > 1:
    myDir = sys.argv[1]
else:
    myDir = os.curdir

items = os.listdir(myDir)  # Fetch all items.
fileList = []  # Initialize empty files array.

# Discriminate files of unrelated formats.
for names in items:
    if "." not in names or names.endswith(".nii") or names.endswith(".dcm"):
        fileList.append(names)

# Make a visual list of the files with assigned numbers to be displayed in terminal.
cnt = 0
selectedFile = ""
for fileName in fileList:
    print(str(cnt) + " - " + fileName)
    cnt = cnt + 1

# Wait for user input, number selects file from displayed menu.
selection = input("Enter file number and hit enter: ")
selectedFile = fileList[int(selection)]

# Read selected image from its file according to the format.
if selectedFile.endswith(".nii"):
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(selectedFile)
elif selectedFile.endswith(".dcm"):
    reader = vtk.vtkDICOMImageReader()
    reader.SetFileName(selectedFile)
else:
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(selectedFile)
reader.Update()

# Initialize Image Viewer 2
imageViewer = vtk.vtkImageViewer2()
imageViewer.SetInputConnection(reader.GetOutputPort())  # Assign image to viewer.
imageViewer.SetSlice(99)  # Set the slice.
imageViewer.SetColorLevel(0.0)  # Set the level.
imageViewer.SetColorWindow(1000.0)  # Set the window.

# Create an accumulate object, assign the image and fetch maximum and minimum intensity values.
accumulate = vtk.vtkImageAccumulate()
accumulate.SetInputConnection(reader.GetOutputPort())
accumulate.Update()
lo = int(accumulate.GetMin()[0])
hi = int(accumulate.GetMax()[0])
colorRange = hi - lo

# Create interactor object and assign it to the viewer.
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
imageViewer.SetupInteractor(renderWindowInteractor)
imageViewer.GetRenderWindow().SetSize(1000, 1000)  # Set the render window size.
imageViewer.GetRenderer().ResetCamera()  # Reset renderer camera.

# Update the text actors for the first time.
set_message()

# Setup an observer for the interactor to register key events.
renderWindowInteractor.AddObserver('KeyPressEvent', change_slice, 1.0)

# Start the interactor.
renderWindowInteractor.Start()
