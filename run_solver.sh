#!/bin/bash

foamCleanTutorials
rm -r 0 > /dev/null 2>&1
rm -rf constant/polyMesh processor*

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

#Running the solver below:
foamRun -solver incompressibleFluid | tee log.solver

foamPostProcess -solver incompressibleFluid -func yPlus -latestTime -noFunctionObjects | tee log.yPlus
