#!/usr/bin/env just --justfile

# Shared commit recipe from fleet-base. Literal path: just does not interpolate variables into import paths.
# Minimal fleet justfile. Recipes are grouped (see fleet-base/templates/justfile.template).
# Run `just --list` to see every recipe.

import 'just/fleet-clean.just'

set shell := ["bash", "-c"]

[group("dev")]
default:
    @just --list

[group("testing")]
test:
    @if [ -d tests ]; then uv run pytest tests/ -v; else echo "no tests/ directory in this repo"; fi

# Pyright ratchet: fails when a file gains errors (scripts in fleet-base; mode from pyproject.toml).
check-types:
    fleet ratchet check

# Unit tests: the gate the pre-push hook runs (fleet hook standard, fleet_base.hook_standard R4)
test-unit:
    just test

# ============================================================================
# Shared fleet recipes, run by fleet-base's installed tool (uv tool install --editable ~/projects/fleet-base).
# Each line calls `fleet recipe NAME`; define a recipe here instead to override it.
# ============================================================================

# Falls back to manual commit if Ollama unavailable or commitmate fails
commit:
    fleet recipe commit

# Add all untracked files and commit with LLM or custom message
commit-all:
    fleet recipe commit-all
