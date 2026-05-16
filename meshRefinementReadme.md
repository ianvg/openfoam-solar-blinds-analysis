# Mesh refinement details
The difference in pressure across the window will be used for the mesh sensitivity analysis.

The mesh sensitivity will primarily be a function of f(blockMesh cell size, refinementRegion level). 

The blockMesh.dict file is the most important when it comes to the necessary refinement of the mesh for the difference. The dx, dy, and dz values control the actual size in meters of the cells in the x, y and z axes. Three different levels of cell sizes are considered.

However, the second variable behind the different levels of meshing is also embedded in the snappyHexMesh.dict file, where the refinementRegion will be used to refine the mesh around the window. Two different levels of refinementRegion are considered.

# Settings for the mesh
## Coarse mesh
dx 1;
dy 1;
dz 1;

refinementRegion

## Medium mesh
dx 0.5;
dy 0.5;
dz 0.5;

## Fine Mesh
dx 0.25;
dy 0.25;
dz 0.25;
