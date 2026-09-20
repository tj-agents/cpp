#!/usr/bin/env bash
# new-gpp-project.sh — scaffold a G++/CMake C++ project.
#
#   new-gpp-project.sh --name <name> --destination <dir> [--cpp-standard 20|23] [--simple] [--dry-run]
#
# Modern (default): libs/core + app + Catch2 tests + CMake presets + clang configs.
# --simple: a single CMakeLists.txt + main.cpp, no library, no tests.
# --dry-run: print what would be created and exit without touching anything.
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd -P)"
template_root="$script_dir/templates"

name=""
destination=""
cpp_standard="23"
simple=0
dry_run=0

usage() {
    echo "usage: new-gpp-project.sh --name <name> --destination <dir> [--cpp-standard 20|23] [--simple] [--dry-run]" >&2
}

while [ $# -gt 0 ]; do
    case "$1" in
        --name) name="${2:-}"; shift 2 ;;
        --destination) destination="${2:-}"; shift 2 ;;
        --cpp-standard) cpp_standard="${2:-}"; shift 2 ;;
        --simple) simple=1; shift ;;
        --dry-run) dry_run=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "new-gpp-project: unknown argument '$1'" >&2; usage; exit 1 ;;
    esac
done

if [ -z "$name" ] || [ -z "$destination" ]; then
    usage
    exit 1
fi

if ! [[ "$name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$ ]]; then
    echo "new-gpp-project: '$name' is not a valid project name (letters, digits, '_', '-', starting with a letter or digit, max 64 chars)" >&2
    exit 1
fi

if [ "$cpp_standard" != "20" ] && [ "$cpp_standard" != "23" ]; then
    echo "new-gpp-project: --cpp-standard must be 20 or 23, got '$cpp_standard'" >&2
    exit 1
fi

if [ ! -d "$destination" ]; then
    echo "new-gpp-project: destination does not exist: $destination" >&2
    exit 1
fi

project_path="$destination/$name"
if [ -e "$project_path" ]; then
    echo "new-gpp-project: Destination already exists: $project_path" >&2
    exit 1
fi

template_subdir="$template_root"
if [ "$simple" -eq 1 ]; then
    template_subdir="$template_root/simple"
fi
if [ ! -d "$template_subdir" ]; then
    echo "new-gpp-project: the packaged G++ templates are missing" >&2
    exit 1
fi

if [ "$simple" -eq 1 ]; then
    mapfile -t templates < <(find "$template_subdir" -type f -name '*.in' | sort)
else
    mapfile -t templates < <(find "$template_subdir" -type f -name '*.in' -not -path "$template_root/simple/*" | sort)
fi
if [ "${#templates[@]}" -eq 0 ]; then
    echo "new-gpp-project: the packaged G++ templates are missing" >&2
    exit 1
fi

# Templates use __PROJECT__ (raw name), __NAMESPACE__ (C++ identifier), __NAMESPACE_UPPER__.
namespace="${name//[^a-zA-Z0-9]/_}"
namespace_upper="$(printf '%s' "$namespace" | tr '[:lower:]' '[:upper:]')"

if [ "$dry_run" -eq 1 ]; then
    echo "new-gpp-project: would create $project_path:"
    for template in "${templates[@]}"; do
        relative="${template#"$template_subdir"/}"
        echo "  ${relative%.in}"
    done
    exit 0
fi

mkdir -p "$project_path"
for template in "${templates[@]}"; do
    relative="${template#"$template_subdir"/}"
    target="$project_path/${relative%.in}"
    mkdir -p "$(dirname -- "$target")"
    sed \
        -e "s/__CPP_STANDARD__/$cpp_standard/g" \
        -e "s/__NAMESPACE_UPPER__/$namespace_upper/g" \
        -e "s/__NAMESPACE__/$namespace/g" \
        -e "s/__PROJECT__/$name/g" \
        "$template" > "$target"
done

if [ "$simple" -eq 1 ]; then
    echo "new-gpp-project: created simple project at $project_path (C++$cpp_standard, G++)"
else
    echo "new-gpp-project: created project at $project_path (C++$cpp_standard, G++)"
    echo "  next: cd $project_path && cmake --preset dev && cmake --build --preset dev && ctest --preset dev"
fi
