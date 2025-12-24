rm db.sqlite3
python manage.py migrate
python manage.py fill_db 1000
python manage.py createcachetable
python manage.py generate_sidebar
python manage.py runserver
