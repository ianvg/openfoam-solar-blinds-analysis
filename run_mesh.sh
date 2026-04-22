#!/bin/bash

//Inspiration for this structure came from the 3D_dampBreak tutorial by Wolf Dynamics World

// To clean out the folder of old run time time-stamps.
foamCleanTutorials 
// Removes the current 0 constants folder.
rm -rf 0
// Copies over the 0_org constants as the new 0 constants folder
cp -r 0_org 0

//blockMesh | tee log.blockMesh
//surfaceFeatures | tee log.surfaceFeatures
//snappyHexMesh -overwrite | tee log.shm
//checkMesh | tee log.checkMesh
// Removes the current 0 constants folder.
rm -rf 0
// Copies over the 0_org constants as the new 0 constants folder
cp -r 0_org 0
//setFields | tee log.setFields
//createPatch -dict system/createPatchDict.0 -overwrite
//createPatch -dict system/createPatchDict.1 -overwrite