## Repository to run and analyse data from LADDIE

Structure of this repository is as follows:

- 'data' contains input geometry data of experiments from ISOMIP or BedMachine data for example
  - 'preprocess_input.ipynb' makes sure the input files have the right format
  - ocean3.nc
  - ocean4.nc
  - BedMachine.nc
  - Crosson-Dotson.nc
  - Pine-Island.nc
  
- 'experiments'
  - 'List_experiments.md' contains different names of experiments and short description of each.
  - 'Experiment_class_X' folders contain experiments with same geometry, with X for example Ocean3, Ocean4, Crosson-Dotson. 
    - 'Experiment_X' folder contains specific experiment config file and output
    
- 'analysis'
  - post-process.py
  - create_anims.ipynb
  - create_plots.ipynb
  - results
    - 'Experiment_X'
      - animations
      - plots
