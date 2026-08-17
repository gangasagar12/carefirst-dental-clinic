#!/usr/bin/env bash

# ==============================================================================
# CareFirst Dental Clinic - Automated Production Build & Deployment Script
# Automatically executes on cloud platforms (Render, Railway, Heroku, etc.)
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "=================================================="
echo " Starting CareFirst Automated Deployment Build   "
echo "=================================================="

# 1. Upgrade pip & Install Dependencies
echo "==> [1/5] Installing Python Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Collect Static Files
echo "==> [2/5] Collecting and Compiling Static Assets..."
python manage.py collectstatic --noinput

# 3. Run Database Migrations
echo "==> [3/5] Applying Database Migrations..."
python manage.py migrate --noinput

# 4. Compile Translation Catalogs (if gettext msgfmt is available)
if command -v msgfmt >/dev/null 2>&1; then
    echo "==> [4/5] Compiling Language Translation Catalogs..."
    python manage.py compilemessages || true
else
    echo "==> [4/5] msgfmt not found, skipping compilemessages."
fi

# 5. Dynamic Data Setup & System Verification
echo "==> [5/5] Executing Dynamic Deployment Initializer (deploy_setup.py)..."
python deploy_setup.py

echo "=================================================="
echo " CareFirst Build & Deployment Completed!         "
echo "=================================================="