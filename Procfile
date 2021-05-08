web: gunicorn ch_settings.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery -A ch_settings worker -l INFO