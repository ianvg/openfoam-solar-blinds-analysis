#!/bin/bash

#######################################################
### Cleaning the case
#######################################################
## Reminder
## Before running anything in parallel, check how processors
## your computer has via lscpu
#######################################################

rm -r 0
#cp -r 0_org 0
rm -rf constant/polyMesh processor*

#######################################################
### Creating and checking the mesh
#######################################################

blockMesh -dict system/blockMeshDict | tee log.blockMesh
#Surface features below intended to extract edges for later selection for
#mesh refinement.
#First copy the .stl so we can extract only the edges related to the window
cp constant/triSurface/interiorSurfaces_30deg_100pct.stl constant/triSurface/interiorSurfacesWindowOnly.stl

surfaceFeatures | tee log.surfaceFeatures #Fixed!

#For running snappyHexMesh for use in the simulation (once you are happy with mesh):
# To write the final snappyHexMesh result directly into constant/polyMesh instead:
snappyHexMesh -overwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

# Running snappyHexMesh in two different passes works better for some reason!
# The first pass only runs the castellation, and snap, and then the second pass only
# runs the addition of the boundary layers
snappyHexMesh -overwrite -dict system/snappyHexMeshDictLayers | tee log.snappyHexMeshLayers

#snappyHexMesh -noOverwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

#Create a zone called all:
createZones | tee log.createZones

#Below to check mesh from mesh in constants/ folder
checkMesh -constant | tee log.checkMesh

# Check the mesh for the number of cell zones.
checkMesh -constant -allTopology | grep "cell zones"
