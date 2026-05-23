#!/bin/bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: bash run_allCases.sh [options]

Run run_all.sh in selected case directories.

Options:
  --case N            Run only case number N. Can be used more than once.
  --first-case N      Run cases with this number or higher.
  --last-case N       Run cases with this number or lower.
  --skip-existing     Skip cases that already have log.masterRun.
  --skip-missing      Skip selected case directories that do not exist.
  --dry-run           Print what would run without running cases.
  -h, --help          Show this help.

Examples:
  bash run_allCases.sh
  bash run_allCases.sh --first-case 25
  bash run_allCases.sh --first-case 25 --last-case 30
  bash run_allCases.sh --case 25 --case 30
  bash run_allCases.sh --first-case 25 --skip-existing
EOF
}

is_int() {
    [[ ${1:-} =~ ^[0-9]+$ ]]
}

case_numbers=()
first_case=""
last_case=""
skip_existing=false
skip_missing=false
dry_run=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --case)
            [[ $# -ge 2 ]] || { echo "ERROR: --case requires a number" >&2; exit 2; }
            is_int "$2" || { echo "ERROR: --case requires a positive integer: $2" >&2; exit 2; }
            case_numbers+=("$2")
            shift 2
            ;;
        --first-case)
            [[ $# -ge 2 ]] || { echo "ERROR: --first-case requires a number" >&2; exit 2; }
            is_int "$2" || { echo "ERROR: --first-case requires a positive integer: $2" >&2; exit 2; }
            first_case="$2"
            shift 2
            ;;
        --last-case)
            [[ $# -ge 2 ]] || { echo "ERROR: --last-case requires a number" >&2; exit 2; }
            is_int "$2" || { echo "ERROR: --last-case requires a positive integer: $2" >&2; exit 2; }
            last_case="$2"
            shift 2
            ;;
        --skip-existing)
            skip_existing=true
            shift
            ;;
        --skip-missing)
            skip_missing=true
            shift
            ;;
        --dry-run)
            dry_run=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

baseDir=$(pwd)

discover_case_numbers() {
    local case_dir case_name number
    for case_dir in "$baseDir"/C[0-9]*; do
        [[ -d "$case_dir" ]] || continue
        case_name=$(basename "$case_dir")
        [[ $case_name =~ ^C([0-9]+)$ ]] || continue
        number="${BASH_REMATCH[1]}"

        if [[ -n $first_case && $number -lt $first_case ]]; then
            continue
        fi
        if [[ -n $last_case && $number -gt $last_case ]]; then
            continue
        fi

        printf '%s\n' "$number"
    done | sort -n
}

range_case_numbers() {
    local start="$1"
    local end="$2"
    local number

    if [[ $start -gt $end ]]; then
        echo "ERROR: --first-case cannot be greater than --last-case" >&2
        exit 2
    fi

    for ((number = start; number <= end; number++)); do
        printf '%s\n' "$number"
    done
}

selected_numbers=()
if [[ ${#case_numbers[@]} -gt 0 ]]; then
    mapfile -t selected_numbers < <(printf '%s\n' "${case_numbers[@]}" | sort -n -u)
elif [[ -n $first_case && -n $last_case ]]; then
    mapfile -t selected_numbers < <(range_case_numbers "$first_case" "$last_case")
else
    mapfile -t selected_numbers < <(discover_case_numbers)
fi

if [[ ${#selected_numbers[@]} -eq 0 ]]; then
    echo "ERROR: No case directories matched the requested selection" >&2
    exit 1
fi

for number in "${selected_numbers[@]}"; do
    case_name="C$number"
    case_dir="$baseDir/$case_name"

    if [[ ! -d "$case_dir" ]]; then
        if [[ $skip_missing == true ]]; then
            echo "$case_name: missing, skipping"
            continue
        fi
        echo "ERROR: Case directory not found: $case_dir" >&2
        exit 1
    fi

    if [[ ! -f "$case_dir/run_all.sh" ]]; then
        if [[ $skip_missing == true ]]; then
            echo "$case_name: run_all.sh missing, skipping"
            continue
        fi
        echo "ERROR: run_all.sh not found in $case_name" >&2
        exit 1
    fi

    if [[ $skip_existing == true && -e "$case_dir/log.masterRun" ]]; then
        echo "$case_name: log.masterRun already exists, skipping"
        continue
    fi

    echo "======================================"
    echo "Running case: $case_name"
    echo "======================================"

    if [[ $dry_run == true ]]; then
        echo "Would run: cd $case_dir && bash run_all.sh 2>&1 | tee log.masterRun"
    else
        (
            cd "$case_dir"
            bash run_all.sh 2>&1 | tee log.masterRun
        )
    fi

    echo "Finished case: $case_name"
    echo
done

echo "All selected cases finished."
