#!/bin/bash

foamPostProcess -solver incompressibleFluid -dict system/externalFunctionObject0 -fields '(U)' -latestTime
