#!/usr/bin/env python3
import argparse
import csv
import math
import re
from pathlib import Path


WINDOW_OPENING_AREA_M2 = 0.936
AIR_DENSITY_KG_M3 = 1.293
FLOW_RATE_FILE = Path("postProcessing/windowOpeningFlowRate/0/surfaceFieldValue.dat")
LINE_SAMPLE_ROOT = Path("postProcessing/sampleDict")
PATCH_DELTA_ROOT = Path("postProcessing/sampleDict1")
DOMAIN_DELTA_ROOT = Path("postProcessing/sampleDict2")


def time_key(value):
    try:
        return float(value)
    except ValueError:
        return value


def time_label(time):
    return f"{time:g}"


def read_openfoam_table(path):
    rows = {}
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            rows[float(parts[0])] = float(parts[1])

    if not rows:
        raise ValueError(f"No data rows found in {path}")

    return rows


def read_flow_rates(case_dir, flow_file):
    path = flow_file if flow_file.is_absolute() else case_dir / flow_file
    if not path.exists():
        raise FileNotFoundError(f"Cannot find flow-rate file: {path}")
    return read_openfoam_table(path)


def read_field_value_delta(case_dir, root, file_name="fieldValueDelta.dat"):
    base = case_dir / root
    if not base.exists():
        raise FileNotFoundError(f"Cannot find fieldValueDelta directory: {base}")

    values = {}
    for time_dir in sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: time_key(p.name)):
        path = time_dir / file_name
        if not path.exists():
            continue

        rows = read_openfoam_table(path)
        values.update(rows)

    if not values:
        raise ValueError(f"No fieldValueDelta values found under {base}")

    return values


def average_column(csv_path, column_name):
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        values = [float(row[column_name]) for row in reader if row.get(column_name)]

    if not values:
        raise ValueError(f"No values found in column {column_name} for {csv_path}")

    return sum(values) / len(values)


def line_number(csv_path):
    match = re.search(r"_(\d+)\.csv$", csv_path.name)
    if not match:
        return None
    return int(match.group(1))


def read_line_pressure_differences(case_dir, sample_root, column_name, pattern):
    base = case_dir / sample_root
    if not base.exists():
        raise FileNotFoundError(f"Cannot find line sample directory: {base}")

    values = {}
    for time_dir in sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: time_key(p.name)):
        csv_paths = sorted(time_dir.glob(pattern))
        if not csv_paths:
            continue

        line_means = {}
        for csv_path in csv_paths:
            number = line_number(csv_path)
            if number is None:
                continue
            line_means[number] = average_column(csv_path, column_name)

        indoor_means = [line_means[number] for number in range(1, 5) if number in line_means]
        outdoor_means = [line_means[number] for number in range(5, 9) if number in line_means]

        if len(indoor_means) != 4 or len(outdoor_means) != 4:
            continue

        indoor_mean = sum(indoor_means) / len(indoor_means)
        outdoor_mean = sum(outdoor_means) / len(outdoor_means)
        values[float(time_dir.name)] = outdoor_mean - indoor_mean

    if not values:
        raise ValueError(f"No complete indoor/outdoor line samples found under {base}")

    return values


def discharge_coefficient(flow_rate, area, rho, pressure_difference):
    delta_p = abs(pressure_difference)
    if delta_p <= 0:
        return math.nan

    return (abs(flow_rate) / area) * math.sqrt(rho / (2.0 * delta_p))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Write a CSV comparing Cd from line, patch, and cellZone "
            "pressure-difference methods."
        )
    )
    parser.add_argument(
        "--case",
        type=Path,
        default=Path("."),
        help="Case directory. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("postProcessing/pressure_cd_summary.csv"),
        help="Output CSV path. Defaults to postProcessing/pressure_cd_summary.csv.",
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
    parser.add_argument(
        "--line-column",
        default="pGaugePa",
        help="Line-sample column to average. Defaults to pGaugePa.",
    )
    parser.add_argument(
        "--line-pattern",
        default="doorPressureLine_*.csv",
        help="Line CSV glob. Defaults to doorPressureLine_*.csv.",
    )
    args = parser.parse_args()

    case_dir = args.case.resolve()
    output_path = args.output if args.output.is_absolute() else case_dir / args.output

    flow_rates = read_flow_rates(case_dir, args.flow_file)
    line_delta_p = read_line_pressure_differences(
        case_dir,
        LINE_SAMPLE_ROOT,
        args.line_column,
        args.line_pattern,
    )
    patch_delta_p = read_field_value_delta(case_dir, PATCH_DELTA_ROOT)
    domain_delta_p = read_field_value_delta(case_dir, DOMAIN_DELTA_ROOT)

    common_times = sorted(
        set(flow_rates)
        & set(line_delta_p)
        & set(patch_delta_p)
        & set(domain_delta_p)
    )
    if not common_times:
        raise ValueError("No common times found across all required post-processing outputs")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "time_s",
                "flow_rate_m3_s",
                "area_m2",
                "rho_kg_m3",
                "pressure_diff_lines_outdoor_minus_indoor_Pa",
                "pressure_diff_patch_outdoor_minus_indoor_Pa",
                "pressure_diff_domains_outside_minus_inside_Pa",
                "Cd_lines",
                "Cd_patch",
                "Cd_domains",
            ],
        )
        writer.writeheader()

        for time in common_times:
            q = flow_rates[time]
            dp_lines = line_delta_p[time]
            dp_patch = patch_delta_p[time]
            dp_domains = domain_delta_p[time]

            writer.writerow(
                {
                    "time_s": time_label(time),
                    "flow_rate_m3_s": f"{q:.9g}",
                    "area_m2": f"{args.area:.9g}",
                    "rho_kg_m3": f"{args.rho:.9g}",
                    "pressure_diff_lines_outdoor_minus_indoor_Pa": f"{dp_lines:.9g}",
                    "pressure_diff_patch_outdoor_minus_indoor_Pa": f"{dp_patch:.9g}",
                    "pressure_diff_domains_outside_minus_inside_Pa": f"{dp_domains:.9g}",
                    "Cd_lines": f"{discharge_coefficient(q, args.area, args.rho, dp_lines):.9g}",
                    "Cd_patch": f"{discharge_coefficient(q, args.area, args.rho, dp_patch):.9g}",
                    "Cd_domains": f"{discharge_coefficient(q, args.area, args.rho, dp_domains):.9g}",
                }
            )

    print(f"Wrote {len(common_times)} row(s) to {output_path}")


if __name__ == "__main__":
    main()
