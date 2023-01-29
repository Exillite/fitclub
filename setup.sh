docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear

docker exec -itd fitclub-web-1 python manage.py bot
docker exec -itd fitclub-web-1 celery -A app worker -l info
docker exec -itd fitclub-web-1 celery -A app beat -l info