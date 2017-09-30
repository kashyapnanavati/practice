# This repository contains all the practice/learning items
Note: 
python --version

# you can even add names of packages after python=3.6 like python=3.6 pandas
conda create --name subscribe python=3.6

# to get into your new environment
source activate subscribe

# Leave your environment
source deactivate

# Remove your environment
conda env remove --name subscribe

# List your environments
conda env list

How to switch between Python2.7 and Python3.6 ?
Currently using conda we have create two env to switch between this
For python3.6 :
source activate py36
source deactivate py36

For python 2.7 :
source activate py27
source deactivate py27



