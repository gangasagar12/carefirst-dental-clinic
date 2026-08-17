#!/usr/bin/env bash

set -o errexit

export PYTHONPATH=.

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate
python scripts/populate_services.py
python scripts/populate_pricing.py
python scripts/populate_blog.py
python scripts/seed_faqs.py
python scripts/seed_testimonials.py