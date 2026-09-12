#!/bin/bash
set -e
cd "$(dirname "$0")"
printf 'Preparando o ambiente...\n'
pip install -r requirements.txt -q
python src/main.py
