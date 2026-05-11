The approximate strategy for the mesh refinement will be to target three levels of mesh refinement: 
1. Coarse
2. Medium
3. Fine

Most of the differences between the three will be programmed in the blockMesh phase of the meshing, and additionally into refinementRegions in snappyHexMesh.

Other snappyHexMesh adjustments (i.e. to castellation, snap layer and boundaries) will be made as necessary so that all three mesh refinement levels are good quality.
