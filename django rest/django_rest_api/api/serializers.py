from rest_framework import serializers
from .models import Image, User, Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ('thumbnail', 'height')


class ImageSerializer(serializers.ModelSerializer):
    thumbnail_set = ThumbnailSerializer(many=True, read_only=True)
    image = serializers.ImageField(write_only=True)
    original_image = serializers.SerializerMethodField()

    def get_original_image(self, obj):
        if obj.user.tier.can_get_full_size_link:
            return obj.image.url

    class Meta:
        model = Image
        fields = ('image', 'thumbnail_set', 'original_image')
        write_only_fields = ('image',)


class GenerateExpiringLinkSerializer(serializers.ModelSerializer):
    image_id = serializers.IntegerField()
    expiration_time = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('image_id', 'expiration_time')
