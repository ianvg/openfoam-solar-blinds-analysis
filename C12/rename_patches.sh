#!/bin/bash

#######################################################
### Renaming the boundary patches
#######################################################
#Rename the outsideMaxX patch to inlet
foamDictionary constant/polyMesh/boundary \
	-entry entry0/outsideMinX -rename inlet

# Rename the insideMaxX patch to outlet
foamDictionary constant/polyMesh/boundary \
	-entry entry0/insideMaxX -rename outlet

# Remove the line "inGroups" from every boundary patch
for patch in $(foamDictionary constant/polyMesh/boundary -entry entry0 -keywords); do
	foamDictionary constant/polyMesh/boundary \
		-entry "entry0/${patch}/inGroups" \
		-remove
done
