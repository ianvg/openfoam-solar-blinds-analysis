#!/bin/bash
#To run use "bash run_solver.sh"
#set -euo pipefail #So we know if the first command out of two piped commands fails, this causes the script to fail adctually!

#Copy over everything from 0_org/ folder to 0/
rm -rf 0
cp -r 0_org 0

#######################################################
### Running the simulation
#######################################################

#Ensure that either the solver in serial or parallel is uncommented.

#Running the solver in serial:
foamRun -solver incompressibleFluid | tee log.solver

#Running the solver in parallel:

#Decomposing the mesh to prepare it for running in parallel
#Ensure that you have the minimum number of processors available for this job before running it!
#Reminder that this number parameter needs to correspond with the decomposeParDict parameter

#decomposePar -force
#mpirun -np 8 foamRun -solver incompressibleFluid -parallel | tee log.solver
#reconstructPar #To reconstruct the parallel case: 

#######################################################
### Post-processing
#######################################################

#Ensure that either the solver in serial or parallel is uncommented.

#Serial post-processing
#foamPostProcess -solver incompressibleFluid -func yPlus -latestTime -noFunctionObjects | tee log.yPlus

#Parallel post-processing
mpirun -np 8 foamPostProcess -solver incompressibleFluid -func yPlus -latestTime -noFunctionObjects -parallel | tee log.yPlus
reconstructPar #To reconstruct the parallel case: 
