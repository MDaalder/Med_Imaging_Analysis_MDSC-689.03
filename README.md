# MDSC-689.03
- Code and environment for MDSC 689.03 Medical Imaging Analysis Course
- Use terminal on Mac or Command Prompt on Windows for conda (Anaconda Prompt may be better!!)
- Git Bash will have to be used for `git` commands on Windows PC

## Setting up the environment:

1. Install Anaconda with the latest Python 3.0 version
2. Create a directory for the code base i.e. /Users/Courses/MDSC 689.03 and navigate to that directory
3. In the terminal or Git Bash, run `git clone <git url>`
4. Run `conda env create -f environment.yml` to create the conda environment (called imaging) while in the same directory as 2 and 3
5. Activate course environment with `conda activate imaging`
6. Deactivate the course environment with `conda deactivate`

## If setting up the environment from scratch:

Create virtual environments and add packages
  ### If running windows, use the Command Prompt or Anaconda Prompt (best)
  
  #### Update installation
  - `conda update conda`
  - `conda update anaconda`
  
  #### Create course environment
  - `conda create -n <env name> python=3`
  
  #### Install vtk package and others (ITK, pydicom)
  - `<env name>$ conda install vtk`
  - `<env name>$ conda install -c conda-forge itk`
  - `<env name>$ conda install -c conda-forge pydicom`
  
  #### Deactivate Environment
  - `<env name>conda deactivate`
  
  ### Check Installation
  - `conda activate <env name>`
  - `<env name>$ python`
  - `import vtk`
  - `print(vtk.vtkVersion.GetVTKSourceVersion())`
  - 'vtk version 8.2.0'
  
  
