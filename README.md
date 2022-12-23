## Repository to run and analyse data from LADDIE

Structure of this repository is as follows:

- 'data' contains input geometry data of experiments from ISOMIP or BedMachine data for example
  - '0_Generate_singleshelf.ipynb' generates input files of single shelves, also with variable geometry based on Paolo et al. 2022 thinning rates
  - '0_Prep_ISOMIPgeoms.ipynb' makes sure the ISOMIP input files have the right format
  
- 'experiments'
  - 'List_experiments.md' contains different names of experiments and short description of each.
  - 'Experiment_class_X' folders contain experiments with same geometry, with X for example Ocean3, Ocean4, Crosson-Dotson. 
    - 'Experiment_X' folder contains specific experiment config file and output
    
- 'analysis'
  - post-process.ipynb
  - create_anims.ipynb
  - create_plots.ipynb
  - results
    - animations
    - plots
