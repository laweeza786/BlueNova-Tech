web: cd backend && python manage.py migrate && python manage.py seed_db && python manage.py collectstatic --noinput && gunicorn bluenova_erp.wsgi --bind 0.0.0.0:$PORT
