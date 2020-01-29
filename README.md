
**Jinja2Parser Web Tool

A web app for parsing Jinja2 templates using variables from a YAML file. Works standalone and/or can synchronise with template and variable files stored on a Git repository (GitHub or Gitea). Repository are added 

docker-compose up -d --build
docker exec jinja2parser python manage.py collectstatic --noinput
docker exec jinja2parser python manage.py migrate --noinput 
docker exec jinja2parser python manage.py makemigrations main --noinput
docker exec jinja2parser python manage.py migrate main --noinput 
docker exec jinja2parser python manage.py createsuperuser --username admin --email <email> --noinput
