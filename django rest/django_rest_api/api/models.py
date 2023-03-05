from django.db import models
from django.contrib.auth.models import AbstractUser
from django_mysql.models import ListCharField
from django.core.validators import MaxValueValidator, MinValueValidator
from PIL import Image as PillowImage
from io import BytesIO
from django.core.files.base import ContentFile
import time
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.signing import Signer
from django.conf import settings
# Create your models here.


class UserTier(models.Model):
    tier = models.CharField(max_length=50)
    allowed_thumbnail_size = ListCharField(
        base_field=models.IntegerField(default=200, validators=[
            MaxValueValidator(10000),
            MinValueValidator(1)
        ]),
        size=6,
        max_length=(6 * 6),
    )
    can_get_full_size_link = models.BooleanField()
    can_create_expiring_link = models.BooleanField()

    def __str__(self) -> str:
        return self.tier


class User(AbstractUser):
    tier = models.ForeignKey(
        UserTier, on_delete=models.SET_DEFAULT, default=1)


class Image(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_images/original',
                              default=None, blank=True, null=True)
    expiration = models.PositiveIntegerField(null=True, blank=True)

    def generate_expiring_link(self, expiration_time):
        signer = Signer()
        expiration = int(time.time()) + expiration_time
        self.expiration = expiration
        signed_value = signer.sign(str(self.id) + '|' + str(expiration))
        self.save()
        return settings.EXPIRING_LINK_BASE_URL + '/' + signed_value

    def create_thumbnail(self, size):
        img = PillowImage.open(self.image)
        width = size
        height = size
        thumbnail = img.copy()
        thumbnail.thumbnail((width, height))
        buffer = BytesIO()
        thumbnail.save(buffer, "PNG")
        content = ContentFile(buffer.getvalue())
        thumbnail_name = os.path.basename(self.image.name)
        Thumbnail.objects.create(
            height=size, original_image=self, thumbnail=InMemoryUploadedFile(content, None, f'{size}px{thumbnail_name}', 'image/png', content.tell, None))

    def __str__(self):
        return f"Image {self.id} uploaded by {self.user.username}"


class Thumbnail(models.Model):
    thumbnail = models.ImageField(upload_to='user_images/thumbnails',
                                  default=None, blank=True, null=True)
    height = models.IntegerField()
    original_image = models.ForeignKey(
        Image, on_delete=models.CASCADE)
