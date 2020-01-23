# MDSC-689.03
- Code and environment for MDSC 689.03 Medical Imaging Analysis Course
- Use terminal for Mac, or Command Prompt for Windows (Anaconda Prompt may be better!!)

## Setting up the environment:

1. Install Anaconda with the latest Python 3.0 version
2. Create a directory for the code base i.e. /Users/Courses/MDSC 689.03 and navigate to that directory
3. In the terminal or Command Prompt (Anaconda Prompt may be better), run `git clone <git url>`
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
  - `<env name>conda install vtk`
  - `<env name>conda install -c conda-forge itk`
  - `<env name>conda install -c conda-forge pydicom`
  
  #### Deactivate Environment
  - `<env name>conda deactivate`
  
