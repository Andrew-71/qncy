docker build .
docker compose up -d
sleep 2
docker exec vk-web-web-1 python manage.py makemigrations
docker exec vk-web-web-1 python manage.py migrate
docker exec vk-web-web-1 python manage.py fill_db 25
