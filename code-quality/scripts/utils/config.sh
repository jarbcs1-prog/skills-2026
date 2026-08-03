#!/bin/bash
# Config parsing utilities for code-quality.
# Reads .code-quality.yml and exposes values as shell variables.
# Booleans are printed as lowercase "true"/"false" for shell compatibility.

CONFIG_FILE="${1:-.code-quality.yml}"

_py_eval() {
    local key="$1"
    python3 -c "
import yaml, sys
try:
    with open('$CONFIG_FILE') as f:
        config = yaml.safe_load(f)
except Exception:
    config = {}
val = config
for k in '$key'.split('.'):
    if isinstance(val, dict) and k in val:
        val = val[k]
    else:
        val = None
        break
if val is None:
    sys.exit(1)
elif isinstance(val, bool):
    print('true' if val else 'false')
elif val is None:
    print('')
else:
    print(val)
" 2>/dev/null
}

get_config_value() {
    local key="$1"
    _py_eval "$key"
}

get_language_enabled() {
    local lang="$1"
    local val
    val=$(_py_eval "languages.$lang.enabled" 2>/dev/null || echo "true")
    # Normalize: if the key exists and is bool, return it. Default: enabled.
    echo "$val"
}

get_incremental_base() {
    _py_eval "incremental.base" 2>/dev/null || echo "HEAD~1"
}

get_incremental_enabled() {
    _py_eval "incremental.enabled" 2>/dev/null || echo "true"
}

get_config_value_raw() {
    local key="$1"
    python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    config = yaml.safe_load(f)
val = config
for k in '$key'.split('.'):
    if isinstance(val, dict) and k in val:
        val = val[k]
    else:
        val = None
        break
print(val if val is not None else '')
" 2>/dev/null
}