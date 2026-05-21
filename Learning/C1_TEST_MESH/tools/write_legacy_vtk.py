#!/usr/bin/env python3
"""Rewrite a VTK line file as older legacy VTK PolyData."""

"""Run using 

The first vtk is the one obtained directly out of the paraView application.

python3 tools/write_legacy_vtk.py constant/triSurface/line1.vtk constant/triSurface/line1_legacy.vtk

surfaceFeatureConvert constant/triSurface/line1_legacy.vtk constant/triSurface/line1.eMesh


"""
import argparse
import sys

import vtk


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite a VTK PolyData/UnstructuredGrid line file as legacy ASCII VTK."
    )
    parser.add_argument("input", help="input .vtk file")
    parser.add_argument("output", help="output .vtk file")
    parser.add_argument(
        "--version",
        type=int,
        default=42,
        help="legacy VTK file version as major/minor digits, e.g. 42 for 4.2",
    )
    args = parser.parse_args()

    reader = vtk.vtkGenericDataObjectReader()
    reader.SetFileName(args.input)
    reader.Update()

    data = reader.GetOutput()
    if isinstance(data, vtk.vtkPolyData):
        poly_data = data
    elif isinstance(data, vtk.vtkUnstructuredGrid):
        geometry = vtk.vtkGeometryFilter()
        geometry.SetInputData(data)
        geometry.Update()
        poly_data = geometry.GetOutput()
    else:
        data_type = data.GetClassName() if data is not None else "None"
        print(f"Unsupported VTK dataset type: {data_type}", file=sys.stderr)
        return 1

    if poly_data is None or poly_data.GetNumberOfPoints() == 0:
        print(f"No PolyData points read from {args.input}", file=sys.stderr)
        return 1

    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(args.output)
    writer.SetInputData(poly_data)
    writer.SetFileTypeToASCII()
    writer.SetFileVersion(args.version)

    if writer.Write() != 1:
        print(f"Failed to write {args.output}", file=sys.stderr)
        return 1

    print(
        f"Wrote {args.output}: "
        f"{poly_data.GetNumberOfPoints()} points, "
        f"{poly_data.GetNumberOfLines()} lines, "
        f"VTK legacy {args.version // 10}.{args.version % 10}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
