# django-image-api

# Usage


# Setup without Docker
```
cd django_rest_api
pip install -r requirements.txt 
python manage.py runserver 0.0.0.0:8000
```

# Docker Setup
```
cd django_rest_api
docker build . -t image_api
docker run -p 8000:8000 image_api 
```
