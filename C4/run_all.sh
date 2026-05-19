#!/bin/bash

foamCleanTutorials
sh run_mesh.sh
sh rename_patches.sh
sh run_solver.sh
sh run_postprocess.sh
