#!/usr/bin/env python3
"""Collect per-case postprocessing CSV outputs into one CSV.

By default this reads C*/postProcessing/pressure_cd_summary.csv and writes
postprocessing_summary_all_cases.csv in the project root.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


DEFAULT_INPUT = Path("postProcessing") / "pressure_cd_summary.csv"
DEFAULT_OUTPUT = Path("postprocessing_summary_all_cases.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine postprocessing CSV outputs from selected case folders into one CSV.",
        epilog=(
            "Examples:\n"
            "  ./collect_postprocessing_csv.py\n"
            "  ./collect_postprocessing_csv.py --first-case 25\n"
            "  ./collect_postprocessing_csv.py --first-case 25 --last-case 30\n"
            "  ./collect_postprocessing_csv.py --case 25 --case 30\n"
            "  ./collect_postprocessing_csv.py --output results/all_cases.csv"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "CSV path relative to each case directory. "
            f"Default: {DEFAULT_INPUT.as_posix()}."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Combined CSV output path. Default: {DEFAULT_OUTPUT.as_posix()}.",
    )
    parser.add_argument(
        "--case-column",
        default="case",
        help="Name of the leading case column. Default: case.",
    )
    parser.add_argument(
        "--case",
        type=int,
        action="append",
        help=(
            "Collect only this case number. Can be used more than once. "
            "By default, all discovered C<number> folders are collected."
        ),
    )
    parser.add_argument(
        "--first-case",
        type=int,
        help="Collect cases with this number or higher.",
    )
    parser.add_argument(
        "--last-case",
        type=int,
        help="Collect cases with this number or lower.",
    )
    return parser.parse_args()


def discover_case_numbers(root: Path) -> list[int]:
    case_numbers = []
    for path in root.glob("C[0-9]*"):
        if not path.is_dir():
            continue

        case_name = path.name
        if not case_name[1:].isdigit():
            continue

        case_numbers.append(int(case_name[1:]))

    return sorted(case_numbers)


def selected_case_numbers(args: argparse.Namespace, root: Path) -> list[int]:
    if args.case:
        case_numbers = sorted(set(args.case))
    elif args.first_case is not None and args.last_case is not None:
        if args.first_case > args.last_case:
            raise ValueError("--first-case cannot be greater than --last-case")
        case_numbers = list(range(args.first_case, args.last_case + 1))
    else:
        case_numbers = discover_case_numbers(root)

    if args.first_case is not None:
        case_numbers = [number for number in case_numbers if number >= args.first_case]
    if args.last_case is not None:
        case_numbers = [number for number in case_numbers if number <= args.last_case]

    if not case_numbers:
        raise ValueError("No case numbers matched the requested selection")

    return case_numbers


def read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("missing header row")
        return list(reader.fieldnames), list(reader)


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent
    output_path = args.output if args.output.is_absolute() else root / args.output
    try:
        case_numbers = selected_case_numbers(args, root)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected_headers: list[str] | None = None
    combined_rows: list[dict[str, str]] = []
    missing_cases: list[str] = []
    missing_outputs: list[str] = []
    skipped_outputs: list[str] = []

    for case_number in case_numbers:
        case_name = f"C{case_number}"
        case_dir = root / case_name
        csv_path = case_dir / args.input

        if not case_dir.is_dir():
            missing_cases.append(case_name)
            continue
        if not csv_path.is_file():
            missing_outputs.append(f"{case_name}: {display_path(csv_path, root)}")
            continue

        try:
            headers, rows = read_csv_rows(csv_path)
        except (OSError, csv.Error, ValueError) as exc:
            skipped_outputs.append(f"{case_name}: {display_path(csv_path, root)} ({exc})")
            continue

        if expected_headers is None:
            expected_headers = headers
        elif headers != expected_headers:
            skipped_outputs.append(
                f"{case_name}: {display_path(csv_path, root)} (header mismatch)"
            )
            continue

        for row in rows:
            combined_rows.append({args.case_column: case_name, **row})

    if expected_headers is None or not combined_rows:
        print("No postprocessing CSV rows found; combined CSV was not written.", file=sys.stderr)
        print_warnings(missing_cases, missing_outputs, skipped_outputs)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[args.case_column, *expected_headers])
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"Wrote {len(combined_rows)} row(s) to {display_path(output_path, root)}")
    print_warnings(missing_cases, missing_outputs, skipped_outputs)
    return 0


def print_warnings(
    missing_cases: list[str],
    missing_outputs: list[str],
    skipped_outputs: list[str],
) -> None:
    if missing_cases:
        print(f"Missing case directories: {', '.join(missing_cases)}", file=sys.stderr)
    if missing_outputs:
        print("Missing postprocessing CSV outputs:", file=sys.stderr)
        for item in missing_outputs:
            print(f"  {item}", file=sys.stderr)
    if skipped_outputs:
        print("Skipped unreadable or incompatible CSV outputs:", file=sys.stderr)
        for item in skipped_outputs:
            print(f"  {item}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
