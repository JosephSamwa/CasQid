#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py makemigrations
python manage.py migrate

#python manage.py runserver_plus --cert-file ./localhost.pem --key-file ./localhost-key.pem
#https://bootstraptemple.com/p/payment-forms
#https://freefrontend.com/bootstrap-payment-forms/

#https://django-sslserver.readthedocs.io/en/stable/
#pip install django-sslserver
#python manage.py runsslserver --cert ./localhost.cert --key ./localhost.key