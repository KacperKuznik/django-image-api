from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from .serializers import ImageSerializer, GenerateExpiringLinkSerializer
from django.shortcuts import get_object_or_404
from .models import Image, UserTier
from time import time
from django.http import Http404
from django.core.signing import Signer, BadSignature
from django.shortcuts import redirect
# Create your views here.


class ImageView(APIView):
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        user_images = Image.objects.filter(user=user)
        return Response(ImageSerializer(user_images, many=True).data)

    def post(self, request):
        try:
            image = request.data['image']
            serializer = ImageSerializer(data=request.data)
            if (serializer.is_valid(raise_exception=True)):
                image_obj = serializer.save(user=request.user, image=image)
                for size in request.user.tier.allowed_thumbnail_size:
                    image_obj.create_thumbnail(size)
                return Response("successfully uploaded image")
            return Response("Error with uploading image", status=400)
        except:
            return Response("You didn't attach an image", status=422)


class ExpiringLinkView(APIView):
    def get(self, request, signed_value, format=None):
        signer = Signer()
        try:
            unsigned_value = signer.unsign(signed_value)
            image_id, expiration_time = unsigned_value.split('|')
            image = Image.objects.get(id=image_id)
            if int(expiration_time) <= int(time()):
                return Response("The link has expired", status=410)
            return HttpResponseRedirect(image.image.url)
        except (ValueError, Image.DoesNotExist, BadSignature):
            return Response("Invalid link", status=404)


class GenerateExpiringLink(APIView):
    serializer_class = GenerateExpiringLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.tier.can_create_expiring_link:
            expiration_time = int(request.data['expiration_time'])
            image_id = request.data['image_id']
            if expiration_time <= 30000 and expiration_time >= 300:
                user_images = Image.objects.filter(
                    user=request.user).filter(pk=image_id)
                if len(user_images) > 0:
                    return Response(user_images[0].generate_expiring_link(expiration_time), status=200)
                return Response("This image does not exist or was not created by this user", status=400)
            else:
                return Response("Expiration time should be between 300 and 30000 seconds", status=400)
        return Response("This user cannot create expiring links", status=403)
