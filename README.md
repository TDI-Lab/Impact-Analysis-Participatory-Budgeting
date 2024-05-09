# Impact-Aware-Participatory-Budgeting
Comprehensive analysis framework for Participatory Budgeting

This repository features the impact analysis of participatory budgeting instances that was collected from the [PABULIB](http://pabulib.org) repository. This repository is also using voting aggregation functions defined in the [pabutools](https://github.com/Grzesiek3713/pabutools) repository --  which contains models and rules for calculating voting outcome for a given voting instance. The folder pabutools within this repository contains the library files used in the corresponding repository

#### Steps for reproducing the results of the analysis
Required python version: Python3.11

1. Clone the repository and install dependencies defined in environment.yml using conda or requirements.txt using pip
2. Unzip the pabulib_data.zip file and ensure that a folder `pabulib_data` is created containing all the files (stored as standard .pb file) that was used during analysis.
3. Once the dependencies have been installed, execute the `project_winners.py` script. This script parses the voting data contained within .pb files inside `pabulib_data` directory, and calculates the winning outcomes based on UG and MES (add1u). The data from voting instances are collectively written to two different CSV files i.e. `metadata.csv`, `projects.csv`
4. Head over to the notebooks directory and execute any notebook for your analysis!