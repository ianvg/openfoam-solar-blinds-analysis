#!/bin/bash
#To run use "bash run_solver.sh"
set -euo pipefail #So we know if the first command out of two piped commands fails

#######################################################
### Cleaning the case
#######################################################

foamCleanTutorials
rm -r 0 > /dev/null 2>&1
rm -rf constant/polyMesh processor*

#######################################################
### Creating and checking the mesh
#######################################################

blockMesh -dict system/blockMeshDict | tee log.blockMesh
surfaceFeatures | tee log.surfaceFeatures

#For running snappyHexMesh for use in the simulation (once you are happy with mesh):
# To write the final snappyHexMesh result directly into constant/polyMesh instead:
snappyHexMesh -overwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

#Create a zone called all:
createZones | tee log.createZones

#Below to check mesh from mesh in constants/ folder
checkMesh -constant | tee log.checkMesh

checkMesh -constant -allTopology | grep "cell zones"

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
#decomposePar -force
#mpirun -np 4 -solver incompressibleFluid -parallel | tee log.solver
#reconstructPar #To reconstruct the parallel case: 

#######################################################
### Post-processing
#######################################################

foamPostProcess -solver incompressibleFluid -func yPlus -latestTime -noFunctionObjects | tee log.yPlus
