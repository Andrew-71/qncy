#!/bin/sh

printenv > /etc/environment

echo "0 3 * * 1 /opt/venv/bin/python /app/manage.py generate_sidebar >> /var/log/cron.log 2>&1" > /etc/cron.d/django-cron

chmod 0644 /etc/cron.d/django-cron

crontab /etc/cron.d/django-cron

touch /var/log/cron.log

echo "Starting Cron..."
cron && tail -f /var/log/cron.log
