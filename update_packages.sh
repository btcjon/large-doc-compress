#!/bin/bash
uv pip compile pyproject.toml -o requirements.txt
uv pip sync requirements.txt