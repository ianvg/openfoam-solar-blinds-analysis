#!/bin/bash

#######################################################
### Some post-processing
#######################################################


# Sampling along lines for gauge pressure at mid points outwards
foamPostProcess -func sampleDict -latestTime

# inletOutletPressureDrop post-processing
foamPostProcess -func sampleDict1 -latestTime
