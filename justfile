#!/usr/bin/env just --justfile

# Shared commit recipe from fleet-base. Literal path: just does not interpolate variables into import paths.
import "../fleet-base/src/fleet_base/justfiles/shared/commit.just"

# Minimal fleet justfile. Recipes are grouped (see fleet-base/templates/justfile.template).
# Run `just --list` to see every recipe.

set shell := ["bash", "-c"]

[group("dev")]
default:
    @just --list

[group("testing")]
test:
    @if [ -d tests ]; then uv run pytest tests/ -v; else echo "no tests/ directory in this repo"; fi
