#!/bin/bash

#######################################################
### Some post-processing
#######################################################


# Sampling along lines for gauge pressure at mid points outwards
foamPostProcess -func sampleDict -latestTime

# inletOutletPressureDrop post-processing
foamPostProcess -func sampleDict1 -latestTime

# Using python tool to get average of each line
python3 tools/average_pGauge_lines.py

# You can also choose specific times (if they already be sampleDict'd on:
# python3 tools/average_pGauge_lines.py --time 60
# Or choose to target pPa instead:
# python3 tools/average_pGauge_lines.py --column pPa


