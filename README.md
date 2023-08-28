# django-image-api

# Usage
This project is an image hosting service that allows users to easily upload and manage their images. The system provides a user-friendly API, with the option to run the application using Docker Compose for simplified deployment. Users can upload images through HTTP requests and view their uploaded images in a list format.

The service offers three built-in account tiers: Basic, Premium, and Enterprise, each offering distinct features:

##Basic Tier:

Users with the "Basic" plan can upload images and receive a link to a 200px height thumbnail.
##Premium Tier:

Users with the "Premium" plan can upload images and access multiple links:
A 200px height thumbnail.
A 400px height thumbnail.
A link to the original uploaded image.
##Enterprise Tier:

Users with the "Enterprise" plan enjoy enhanced features, including:
A 200px height thumbnail.
A 400px height thumbnail.
A link to the original uploaded image.
The ability to generate expiring links that remain active for a specified duration (between 300 and 30000 seconds).

Administrators have the privilege to create custom tiers, allowing configuration of various parameters:
Thumbnail sizes of their choice.
Inclusion or exclusion of links to the original uploaded file.
The ability to generate expiring links for the images.

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
