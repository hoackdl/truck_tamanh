#!/bin/bash

set -o errexit

# Cập nhật pip và công cụ build để tránh lỗi khi build lxml/reportlab
pip install --upgrade pip setuptools wheel

# Cài dependencies
pip install -r requirements.txt

