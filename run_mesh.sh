#!/bin/bash

foamCleanTutorials
rm -r 0 > /dev/null 2>&1
rm -rf constant/polyMesh processor*

blockMesh -dict system/blockMeshDict | tee log.blockMesh
surfaceFeatures | tee log.surfaceFeatures

# To get the intermediate time-step directories from snappyHexMesh:
snappyHexMesh -noOverwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

# To write the final snappyHexMesh result directly into constant/polyMesh instead:
#snappyHexMesh -overwrite -dict system/snappyHexMeshDict | tee log.snappyHexMesh

checkMesh -latestTime | tee log.checkMesh
