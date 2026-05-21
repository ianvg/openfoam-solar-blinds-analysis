# snappyHexMesh Setup

This case is set up to mesh `constant/triSurface/Window_1.stl` with `snappyHexMesh`.

The STL was checked with:

```bash
surfaceCheck constant/triSurface/Window_1.stl
```

Current STL summary:

- Surface name: `Mesh`
- Bounds: `(0 -2.5 -2.5)` to `(0.1 2.5 2.5)`
- Closed manifold surface: yes

The active `system/blockMeshDict` is a dedicated background box around the STL:

- x range: `-20` to `30`
- y range: `-2.5` to `2.5`
- z range: `-2.5` to `2.5`

The previous room block mesh is preserved as `system/blockMeshDict.room`.

Run the meshing workflow with:

```bash
./run_mesh.sh
```

That script runs:

```bash
blockMesh
surfaceFeatures
snappyHexMesh -overwrite
checkMesh -meshQuality
```

The generated mesh is written to `constant/polyMesh`. Feature extraction writes
`constant/triSurface/Window_1.eMesh` and `constant/extendedFeatureEdgeMesh/`; these are
generated outputs and are ignored by git.

The retained mesh region is selected with:

```foam
locationInMesh (10 0 0);
```

This point is outside the closed STL but inside the +x side of the background box, so
SHM keeps the external fluid region in front of the window and cuts out the solid
window surface as `window_wall`.

The STL is a closed solid frame with a through-opening. The front and behind fluid
regions should therefore remain connected through the opening when snappyHexMesh
resolves the aperture. The `locationInMesh` point can stay on the `+x` side because
that connected fluid region reaches the `-x` side through the opening.

The outer STL edges lie exactly on `y/z = +/-2.5`, matching the requested domain
height and width. If snappyHexMesh later has trouble where the STL coincides with
the domain boundary, add a small clearance around the wall or make those outer
domain patches wall-type boundaries.
