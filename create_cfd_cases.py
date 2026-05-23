#!/usr/bin/env python3
"""Create OpenFOAM cases from caseTemplate using CSV data and STLs.

Run this script from anywhere. It resolves all project paths relative to the
folder containing this file.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CaseConfig:
    case_number: int
    angle_deg: str
    shade_pct: str
    velocity_value: str
    k_value: str
    epsilon_value: str

    @property
    def case_name(self) -> str:
        return f"C{self.case_number}"

    @property
    def stl_name(self) -> str:
        return f"interiorSurfaces_{self.angle_deg}deg_{self.shade_pct}pct.stl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy caseTemplate to case folders and customize each case from CSV/STL data."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete existing target case folders before recreating them.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip case folders that already exist instead of raising an error.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned actions without copying or editing files.",
    )
    parser.add_argument(
        "--case",
        type=int,
        action="append",
        help=(
            "Create only this case number. Can be used more than once. "
            "By default, all cases listed in the CSV are created."
        ),
    )
    parser.add_argument(
        "--first-case",
        type=int,
        help="Create only CSV cases with this number or higher.",
    )
    parser.add_argument(
        "--last-case",
        type=int,
        help="Create only CSV cases with this number or lower.",
    )
    parser.add_argument(
        "--source-case",
        default="caseTemplate",
        help="Source case folder name. Default: caseTemplate.",
    )
    parser.add_argument(
        "--csv",
        default="experimentalCFDTurbulenceConditions.csv",
        help="CSV filename relative to this script. Default: experimentalCFDTurbulenceConditions.csv.",
    )
    parser.add_argument(
        "--stl-dir",
        default="STL",
        help="STL folder relative to this script. Default: STL.",
    )
    return parser.parse_args()


def clean_cell(value: str) -> str:
    return value.strip().lstrip("\ufeff")


def numeric_text(value: str) -> str:
    """Return digits/decimal/scientific notation from a CSV value."""
    cleaned = clean_cell(value)
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?", cleaned)
    if not match:
        raise ValueError(f"Could not parse numeric value from {value!r}")
    return match.group(0)


def format_number(value: float) -> str:
    if math.isclose(value, round(value), rel_tol=0, abs_tol=1e-9):
        return str(int(round(value)))
    return f"{value:.12g}"


def shade_percent_text(value: str) -> str:
    """Convert CSV shade openings to the percentage text used in STL names."""
    shade = float(numeric_text(value))
    if 0 <= shade <= 1:
        shade *= 100
    return format_number(shade)


def read_csv_rows(csv_path: Path) -> list[list[str]]:
    with csv_path.open("rb") as raw_handle:
        is_gzip = raw_handle.read(2) == b"\x1f\x8b"

    opener = gzip.open if is_gzip else open
    encodings = ("utf-8-sig", "cp1252", "latin-1")
    last_error: UnicodeDecodeError | None = None
    for encoding in encodings:
        try:
            with opener(csv_path, mode="rt", newline="", encoding=encoding) as handle:
                return list(csv.reader(handle))
        except UnicodeDecodeError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise ValueError(f"Could not read CSV rows from {csv_path}")


def load_case_configs(csv_path: Path) -> dict[int, CaseConfig]:
    rows = read_csv_rows(csv_path)

    if not rows:
        raise ValueError(f"{csv_path} is empty")

    headers = [clean_cell(header) for header in rows[0]]
    required = {
        "Window opening angle (degrees)",
        "Shade opening (%)",
        "Representative mean velocity (m/s)",
        "k value",
        "Epsilon",
    }
    missing = sorted(required.difference(headers))
    if missing:
        raise ValueError(f"{csv_path} is missing required column(s): {', '.join(missing)}")

    angle_idx = headers.index("Window opening angle (degrees)")
    shade_idx = headers.index("Shade opening (%)")
    velocity_idx = headers.index("Representative mean velocity (m/s)")
    k_idx = headers.index("k value")
    epsilon_idx = headers.index("Epsilon")

    configs: dict[int, CaseConfig] = {}
    for row in rows[1:]:
        if not row or not clean_cell(row[0]):
            continue

        case_match = re.fullmatch(r"Case\s+(\d+)", clean_cell(row[0]), re.IGNORECASE)
        if not case_match:
            continue

        case_number = int(case_match.group(1))
        configs[case_number] = CaseConfig(
            case_number=case_number,
            angle_deg=numeric_text(row[angle_idx]),
            shade_pct=shade_percent_text(row[shade_idx]),
            velocity_value=numeric_text(row[velocity_idx]),
            k_value=numeric_text(row[k_idx]),
            epsilon_value=numeric_text(row[epsilon_idx]),
        )

    if not configs:
        raise ValueError(f"{csv_path} does not contain any rows named like 'Case 1'")

    return configs


def selected_case_numbers(args: argparse.Namespace, configs: dict[int, CaseConfig]) -> list[int]:
    if args.case:
        missing = sorted(set(args.case).difference(configs))
        if missing:
            missing_names = ", ".join(f"Case {number}" for number in missing)
            raise ValueError(f"Requested case(s) not found in CSV: {missing_names}")
        case_numbers = sorted(set(args.case))
    else:
        case_numbers = sorted(configs)

    if args.first_case is not None:
        case_numbers = [number for number in case_numbers if number >= args.first_case]
    if args.last_case is not None:
        case_numbers = [number for number in case_numbers if number <= args.last_case]

    if not case_numbers:
        raise ValueError("No CSV cases matched the requested selection")

    return case_numbers


def copy_case(source: Path, target: Path, overwrite: bool, dry_run: bool) -> None:
    if target.exists():
        if not overwrite:
            raise FileExistsError(
                f"{target} already exists. Re-run with --overwrite to recreate it."
            )
        if dry_run:
            print(f"Would remove existing {target}")
        else:
            shutil.rmtree(target)

    ignored = shutil.ignore_patterns(".git", ".codex", ".agents", "__pycache__")
    if dry_run:
        print(f"Would copy {source} -> {target}")
    else:
        shutil.copytree(source, target, ignore=ignored)


def install_stl(case_dir: Path, stl_source: Path, stl_name: str, dry_run: bool) -> None:
    tri_surface_dir = case_dir / "constant" / "triSurface"
    old_stl = tri_surface_dir / "interiorSurfaces.stl"
    new_stl = tri_surface_dir / stl_name

    if dry_run:
        print(f"Would copy {stl_source} -> {new_stl}")
        if old_stl != new_stl:
            print(f"Would remove {old_stl}")
        return

    tri_surface_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(stl_source, new_stl)
    if old_stl.exists() and old_stl != new_stl:
        old_stl.unlink()


def replace_text(path: Path, replacements: dict[str, str], dry_run: bool) -> None:
    if not path.exists():
        return

    original = path.read_text(encoding="utf-8")
    updated = original
    for old, new in replacements.items():
        updated = updated.replace(old, new)

    if updated == original:
        return

    if dry_run:
        print(f"Would update references in {path}")
    else:
        path.write_text(updated, encoding="utf-8")


def update_surface_references(case_dir: Path, stl_name: str, dry_run: bool) -> None:
    if dry_run and not case_dir.exists():
        print(
            "Would update interiorSurfaces.stl references in "
            f"{case_dir / 'system' / 'snappyHexMeshDict'}, "
            f"{case_dir / 'system' / 'snappyHexMeshDictLayers'}, and "
            f"{case_dir / 'system' / 'surfaceFeaturesDict'}, and "
            f"{case_dir / 'run_mesh.sh'}"
        )
        return

    replacements = {"interiorSurfaces.stl": stl_name}
    for relative_path in (
        "run_mesh.sh",
        "system/snappyHexMeshDict",
        "system/snappyHexMeshDictLayers",
        "system/surfaceFeaturesDict",
    ):
        replace_text(case_dir / relative_path, replacements, dry_run)


def set_openfoam_constant(path: Path, name: str, value: str, dry_run: bool) -> None:
    original = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"(?m)^(\s*{re.escape(name)}\s+)[^;]+;")
    updated, count = pattern.subn(rf"\g<1>{value};", original)

    if count == 0:
        raise ValueError(f"Could not find {name} declaration in {path}")

    if dry_run:
        print(f"Would set {name} = {value} in {path}")
    else:
        path.write_text(updated, encoding="utf-8")


def format_float(value: float) -> str:
    return f"{value:.12g}"


def scaled_vector(vector_text: str, magnitude_text: str) -> str:
    components = [float(component) for component in vector_text.split()]
    if len(components) != 3:
        raise ValueError(f"Expected a 3-component vector, got ({vector_text})")

    current_magnitude = math.sqrt(sum(component * component for component in components))
    if current_magnitude == 0:
        raise ValueError("Cannot preserve direction from a zero-magnitude outlet velocity")

    target_magnitude = float(magnitude_text)
    scaled = [
        component / current_magnitude * target_magnitude for component in components
    ]
    return " ".join(format_float(component) for component in scaled)


def set_outlet_velocity(path: Path, magnitude: str, dry_run: bool) -> None:
    original = path.read_text(encoding="utf-8")
    outlet_match = re.search(r"(?ms)^(\s*outlet\s*\{)(.*?)(^\s*\})", original)
    if not outlet_match:
        raise ValueError(f"Could not find outlet boundary block in {path}")

    outlet_body = outlet_match.group(2)
    value_pattern = re.compile(r"(?m)^(\s*value\s+uniform\s*)\(([^)]*)\)(\s*;)")
    value_match = value_pattern.search(outlet_body)
    if not value_match:
        raise ValueError(f"Could not find active outlet value uniform vector in {path}")

    vector = scaled_vector(value_match.group(2), magnitude)
    updated_body = (
        outlet_body[: value_match.start()]
        + f"{value_match.group(1)}({vector}){value_match.group(3)}"
        + outlet_body[value_match.end() :]
    )
    updated = (
        original[: outlet_match.start(2)]
        + updated_body
        + original[outlet_match.end(2) :]
    )

    if dry_run:
        print(f"Would set outlet velocity magnitude = {magnitude} in {path}")
    else:
        path.write_text(updated, encoding="utf-8")


def update_velocity_fields(case_dir: Path, config: CaseConfig, dry_run: bool) -> None:
    velocity_vector = f"({config.velocity_value} 0 0)"

    if dry_run:
        print(
            f"Would set velocityConstant={velocity_vector} "
            f"in all copied U files under {case_dir}"
        )
        return

    velocity_files = sorted(path for path in case_dir.rglob("U") if path.is_file())
    if not velocity_files:
        raise FileNotFoundError(f"No U files found under {case_dir}")

    for path in velocity_files:
        set_openfoam_constant(path, "velocityConstant", velocity_vector, dry_run)


def update_turbulence_fields(case_dir: Path, config: CaseConfig, dry_run: bool) -> None:
    if dry_run and not case_dir.exists():
        print(
            f"Would set kConstant={config.k_value} and "
            f"epsilonConstant={config.epsilon_value} in all copied k/epsilon files under {case_dir}"
        )
        return

    k_files = sorted(path for path in case_dir.rglob("k") if path.is_file())
    epsilon_files = sorted(path for path in case_dir.rglob("epsilon") if path.is_file())

    if not k_files:
        raise FileNotFoundError(f"No k files found under {case_dir}")
    if not epsilon_files:
        raise FileNotFoundError(f"No epsilon files found under {case_dir}")

    for path in k_files:
        set_openfoam_constant(path, "kConstant", config.k_value, dry_run)
    for path in epsilon_files:
        set_openfoam_constant(path, "epsilonConstant", config.epsilon_value, dry_run)


def main() -> None:
    args = parse_args()
    if args.overwrite and args.skip_existing:
        raise ValueError("--overwrite and --skip-existing cannot be used together")

    root = Path(__file__).resolve().parent
    source_case = root / args.source_case
    csv_path = root / args.csv
    stl_dir = root / args.stl_dir

    if not source_case.is_dir():
        raise FileNotFoundError(f"Source case folder not found: {source_case}")
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    if not stl_dir.is_dir():
        raise FileNotFoundError(f"STL folder not found: {stl_dir}")

    configs = load_case_configs(csv_path)

    case_numbers = selected_case_numbers(args, configs)
    for case_number in case_numbers:
        config = configs[case_number]
        stl_source = stl_dir / config.stl_name
        if not stl_source.is_file():
            raise FileNotFoundError(f"Expected STL not found for {config.case_name}: {stl_source}")

        case_dir = root / config.case_name
        if case_dir.exists() and args.skip_existing:
            print(f"{config.case_name}: already exists, skipping")
            continue

        print(
            f"{config.case_name}: {config.stl_name}, "
            f"Uout={config.velocity_value}, k={config.k_value}, "
            f"epsilon={config.epsilon_value}"
        )
        copy_case(source_case, case_dir, args.overwrite, args.dry_run)
        install_stl(case_dir, stl_source, config.stl_name, args.dry_run)
        update_surface_references(case_dir, config.stl_name, args.dry_run)
        update_velocity_fields(case_dir, config, args.dry_run)
        update_turbulence_fields(case_dir, config, args.dry_run)


if __name__ == "__main__":
    main()
