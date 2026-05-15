#!/bin/bash

foamPostProcess -solver incompressibleFluid -dict system/externalFunctionObject0 -fields '(U)' -latestTime

foamPostProcess -solver incompressibleFluid -dict system/externalFunctionObject1 -fields '(U)' -latestTime

foamPostProcess -solver incompressibleFluid -dict system/externalFunctionObject2 -fields '(U)' -latestTime
