#!/bin/bash

#######################################################
### Some post-processing
#######################################################


# Sampling along lines for gauge pressure at mid points outwards
foamPostProcess -func sampleDict -latestTime

# inletOutletPressureDrop post-processing
foamPostProcess -func sampleDict1 -latestTime

# Average indoor-minus-outdoor pressure difference from pGaugePa using cellZones
foamPostProcess -func sampleDict2 -latestTime
# Average indoor-minu-outdoor pressure difference from pGaugePa using cellZones
#foamPostProcess -func sampleDict2 -noZero

# Using python tool to get average differential pressure of each line
python3 tools/average_pGauge_lines.py

# Write flow-rate, pressure-difference and Cd comparison CSV
python3 tools/write_pressure_cd_summary.py

# You can also choose specific times (if they already be sampleDict'd on:
# python3 tools/average_pGauge_lines.py --time 60
# Or choose to target pPa instead:
# python3 tools/average_pGauge_lines.py --column pPa


#Now delete the processor folder, unless we need to restart from decomposed results.
rm -rf processor*
