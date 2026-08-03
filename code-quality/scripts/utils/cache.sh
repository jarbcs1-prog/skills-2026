#!/bin/bash
# File hash caching and changed-file detection for incremental mode.
# Stores SHA256 hashes of checked files to skip unchanged files on re-runs.

CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/code-quality"
CACHE_FILE="$CACHE_DIR/file_hashes.txt"

mkdir -p "$CACHE_DIR"

hash_file() {
    local file="$1"
    sha256sum "$file" 2>/dev/null | awk '{print $1}'
}

get_cached_hash() {
    local file="$1"
    grep "^$file:" "$CACHE_FILE" 2>/dev/null | head -1 | cut -d: -f2
}

store_hash() {
    local file="$1"
    local hash="$2"
    local tmp
    tmp=$(mktemp)
    grep -v "^$file:" "$CACHE_FILE" 2>/dev/null > "$tmp" || true
    echo "$file:$hash" >> "$tmp"
    mv "$tmp" "$CACHE_FILE"
}

is_changed() {
    local file="$1"
    local current_hash
    current_hash=$(hash_file "$file")
    local cached_hash
    cached_hash=$(get_cached_hash "$file")
    if [ "$current_hash" != "$cached_hash" ]; then
        store_hash "$file" "$current_hash"
        return 0
    fi
    return 1
}

clear_cache() {
    rm -f "$CACHE_FILE"
}

list_cached_files() {
    cut -d: -f1 "$CACHE_FILE" 2>/dev/null || true
}

changed_files() {
    local base="${1:-HEAD~1}"
    shift
    local extensions=("$@")
    local git_output
    git_output=$(git diff --name-only "$base" 2>/dev/null || true)
    if [ -z "$git_output" ]; then
        return 0
    fi
    local count=0
    while IFS= read -r file; do
        [ -z "$file" ] && continue
        local matches=false
        for ext in "${extensions[@]}"; do
            case "$file" in
                *."$ext")
                    matches=true
                    break
                    ;;
            esac
        done
        if [ "$matches" = "true" ]; then
            if [ -z "${result:-}" ]; then
                result="$file"
            else
                result="$result"$'\n'"$file"
            fi
            count=$((count + 1))
        fi
    done <<< "$git_output"
    echo "$result"
    return 0
}