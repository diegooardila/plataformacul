#!/usr/bin/env bash
set -o errexit

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias del frontend y buildear
cd frontend
npm install
npm run build
cd ..
