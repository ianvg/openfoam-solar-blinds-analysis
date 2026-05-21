#!/usr/bin/env python3
import argparse
import csv
import math
import re
from pathlib import Path


WINDOW_OPENING_AREA_M2 = 0.936  # 1.04 m x 0.9 m
AIR_DENSITY_KG_M3 = 1.293
FLOW_RATE_FILE = Path("postProcessing/windowOpeningFlowRate/0/surfaceFieldValue.dat")


def time_key(path):
    try:
        return float(path.name)
    except ValueError:
        return path.name


def latest_sample_dir(root):
    sample_root = root / "postProcessing" / "sampleDict"
    time_dirs = [path for path in sample_root.iterdir() if path.is_dir()]
    if not time_dirs:
        raise FileNotFoundError(f"No time directories found under {sample_root}")
    return max(time_dirs, key=time_key)


def average_column(csv_path, column_name):
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        values = [float(row[column_name]) for row in reader if row.get(column_name)]

    if not values:
        raise ValueError(f"No values found in column {column_name} for {csv_path}")

    return sum(values) / len(values)


def read_flow_rate(case_dir, flow_file, requested_time):
    path = flow_file if flow_file.is_absolute() else case_dir / flow_file
    if not path.exists():
        raise FileNotFoundError(f"Cannot find flow-rate file: {path}")

    rows = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 2:
                continue
            rows.append((float(parts[0]), float(parts[1])))

    if not rows:
        raise ValueError(f"No flow-rate values found in {path}")

    if requested_time is not None:
        target = float(requested_time)
        for time, flow_rate in rows:
            if math.isclose(time, target, rel_tol=0.0, abs_tol=1e-9):
                return time, flow_rate
        raise ValueError(f"No flow-rate value found for time {requested_time} in {path}")

    return rows[-1]


def line_number(csv_path):
    match = re.search(r"_(\d+)\.csv$", csv_path.name)
    if not match:
        return None
    return int(match.group(1))


def main():
    parser = argparse.ArgumentParser(
        description="Average pGaugePa along each sampled line, then average the line means."
    )
    parser.add_argument(
        "--case",
        type=Path,
        default=Path("."),
        help="Case directory. Defaults to the current directory.",
    )
    parser.add_argument(
        "--time",
        help="Sample time directory to read. Defaults to the latest sampleDict time.",
    )
    parser.add_argument(
        "--pattern",
        default="doorPressureLine_*.csv",
        help="CSV filename glob. Defaults to doorPressureLine_*.csv.",
    )
    parser.add_argument(
        "--column",
        default="pGaugePa",
        help="Column to average. Defaults to pGaugePa.",
    )
    parser.add_argument(
        "--area",
        type=float,
        default=WINDOW_OPENING_AREA_M2,
        help=f"Window opening area in m2. Defaults to {WINDOW_OPENING_AREA_M2}.",
    )
    parser.add_argument(
        "--rho",
        type=float,
        default=AIR_DENSITY_KG_M3,
        help=f"Air density in kg/m3. Defaults to {AIR_DENSITY_KG_M3}.",
    )
    parser.add_argument(
        "--flow-file",
        type=Path,
        default=FLOW_RATE_FILE,
        help=f"Flow-rate file. Defaults to {FLOW_RATE_FILE}.",
    )
    args = parser.parse_args()

    case_dir = args.case.resolve()
    sample_dir = (
        case_dir / "postProcessing" / "sampleDict" / args.time
        if args.time
        else latest_sample_dir(case_dir)
    )

    csv_paths = sorted(sample_dir.glob(args.pattern))
    if not csv_paths:
        raise FileNotFoundError(f"No files matching {args.pattern} in {sample_dir}")

    line_means = {}
    for csv_path in csv_paths:
        number = line_number(csv_path)
        if number is None:
            print(f"Skipping {csv_path.name}: expected a name like doorPressureLine_01.csv")
            continue

        mean = average_column(csv_path, args.column)
        line_means[number] = mean
        print(f"{csv_path.name}: mean({args.column}) = {mean:.6g}")

    indoor_means = [line_means[number] for number in range(1, 5) if number in line_means]
    outdoor_means = [line_means[number] for number in range(5, 9) if number in line_means]

    if len(indoor_means) != 4:
        raise ValueError("Expected indoor lines 01-04")
    if len(outdoor_means) != 4:
        raise ValueError("Expected outdoor lines 05-08")

    indoor_mean = sum(indoor_means) / len(indoor_means)
    outdoor_mean = sum(outdoor_means) / len(outdoor_means)
    pressure_difference = outdoor_mean - indoor_mean
    delta_p = abs(pressure_difference)
    flow_time, flow_rate = read_flow_rate(case_dir, args.flow_file, args.time)
    flow_rate_magnitude = abs(flow_rate)

    if delta_p <= 0:
        raise ValueError("Pressure difference must be non-zero to calculate Cd")

    discharge_coefficient = (flow_rate_magnitude / args.area) * math.sqrt(
        args.rho / (2.0 * delta_p)
    )

    print()
    print(f"Indoor average of line means 01-04 = {indoor_mean:.6g}")
    print(f"Outdoor average of line means 05-08 = {outdoor_mean:.6g}")
    print(f"Outdoor - indoor = {pressure_difference:.6g}")
    print()
    print(f"Q at time {flow_time:g} = {flow_rate:.6g} m3/s")
    print(f"|Q| = {flow_rate_magnitude:.6g} m3/s")
    print(f"Area = {args.area:.6g} m2")
    print(f"rho = {args.rho:.6g} kg/m3")
    print(f"Cd = {discharge_coefficient:.6g}")


if __name__ == "__main__":
    main()
