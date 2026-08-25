#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
compile)
  mapfile -t files < <(find . -type f -name 'week_*.tex' ! -path './.git/*' | sed 's|^\./||' | sort)
  if ((${#files[@]} == 0)); then
    echo "::error::No week_*.tex files found"
    exit 1
  fi
  for file in "${files[@]}"; do
    uv run latex-compile "$file"
  done
  ;;
package)
  mkdir -p dist
  declare -A weeks=()
  latest=0
  while IFS= read -r pdf; do
    dir=$(dirname "$pdf")
    base=$(basename "$pdf" .pdf)
    [[ "$base" =~ ^week_0*([0-9]+)$ ]] || continue
    num=${BASH_REMATCH[1]}
    if ((num > latest)); then
      latest=$num
    fi
    mkdir -p "dist/.staging/${dir}"
    cp "$pdf" "dist/.staging/${dir}/W${num}.pdf"
    weeks["$dir"]=1
  done < <(find . -type f -name 'week_*.pdf' ! -path './.git/*' ! -path './dist/*' | sed 's|^\./||' | sort)

  if ((${#weeks[@]} == 0)); then
    echo "::error::No week_*.pdf outputs to package"
    exit 1
  fi

  for dir in "${!weeks[@]}"; do
    zip_name="$(basename "$dir").zip"
    (cd "dist/.staging/${dir}" && zip -X -q "../../${zip_name}" W*.pdf)
    echo "packed dist/${zip_name}:"
    unzip -l "dist/${zip_name}"
  done
  rm -rf dist/.staging
  echo "week=$latest" >> "$GITHUB_OUTPUT"
  ;;
*)
  echo "usage: $0 {compile|package}" >&2
  exit 2
  ;;
esac
