#!/bin/bash

foamCleanTutorials
rm -r 0 > /dev/null 2>&1
rm -rf constant/polyMesh processor*

blockMesh -dict system/blockMeshDict | tee log.blockMesh
surfaceFeatures | tee log.surfaceFeatures

# To get the intermediate time-step directories for troubleshooting from snappyHexMesh:
#snappyHexMesh -noOverwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

#For running snappyHexMesh for use in the simulation (once you are happy with mesh):
snappyHexMesh -overwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

# To write the final snappyHexMesh result directly into constant/polyMesh instead:
#snappyHexMesh -overwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

#Create a zone called all:
createZones | tee log.createZones

#Below to check mesh from intermediate troubleshooting
checkMesh -latestTime | tee log.checkMesh

checkMesh -constant -allTopology | grep "cell zones"
