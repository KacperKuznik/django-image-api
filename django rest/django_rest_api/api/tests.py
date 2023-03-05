from django.test import TestCase
from api.models import User, Image, UserTier, Thumbnail
from django.urls import reverse
from time import time
from django.core.signing import Signer
from django.core.files.uploadedfile import SimpleUploadedFile
# Create your tests here.


class ImageViewTestCase(TestCase):
    def setUp(self):
        self.basic = UserTier.objects.create(tier='Basic', allowed_thumbnail_size=[
            200], can_get_full_size_link=False, can_create_expiring_link=False)
        self.basic_user = User.objects.create(
            username='BasicUser', password='123', tier=self.basic)
        self.premium = UserTier.objects.create(tier='Premium', allowed_thumbnail_size=[
            200, 400], can_get_full_size_link=True, can_create_expiring_link=False)
        self.premium_user = User.objects.create(
            username='PremiumUser', password='123', tier=self.premium)
        small_img = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.image = SimpleUploadedFile(
            'small.png', small_img, content_type='image/png')

    def test_get_images_not_logged(self):
        response = self.client.get(reverse('ImageView'))
        self.assertEqual(response.status_code, 403)

    def test_get_images_logged(self):
        self.client.force_login(self.basic_user)
        response = self.client.get(reverse('ImageView'))
        self.assertEqual(response.status_code, 200)

    def test_upload_no_image(self):
        self.client.force_login(self.basic_user)
        response = self.client.post(reverse('ImageView'))
        self.assertEqual(response.status_code, 422)

    def test_upload_image(self):
        self.client.force_login(self.basic_user)
        self.assertEqual(len(Image.objects.all()), 0)
        response = self.client.post(
            reverse('ImageView'), data={'image': self.image})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Image.objects.all()), 1)

    def test_create_thumbnails_basic(self):
        self.client.force_login(self.basic_user)
        self.assertEqual(len(Thumbnail.objects.all()), 0)
        response = self.client.post(
            reverse('ImageView'), data={'image': self.image})
        self.assertEqual(len(Thumbnail.objects.all()), 1)

    def test_create_thumbnails_premium(self):
        self.client.force_login(self.premium_user)
        self.assertEqual(len(Thumbnail.objects.all()), 0)
        response = self.client.post(
            reverse('ImageView'), data={'image': self.image})
        self.assertEqual(len(Thumbnail.objects.all()), 2)

    def test_get_original_link_basic(self):
        self.client.force_login(self.basic_user)
        response = self.client.post(
            reverse('ImageView'), data={'image': self.image})
        response = self.client.get(reverse('ImageView'))
        self.assertEqual(response.data[0]['original_image'], None)

    def test_get_original_link_premium(self):
        self.client.force_login(self.premium_user)
        response = self.client.post(
            reverse('ImageView'), data={'image': self.image})
        response = self.client.get(reverse('ImageView'))
        self.assertIsNotNone(response.data[0]['original_image'])


class GenerateExpiringLinksTestCase(TestCase):
    def setUp(self):
        self.basic = UserTier.objects.create(tier='Basic', allowed_thumbnail_size=[
            200], can_get_full_size_link=False, can_create_expiring_link=False)
        self.basic_user = User.objects.create(
            username='BasicUser', password='123', tier=self.basic)
        self.premium = UserTier.objects.create(tier='Premium', allowed_thumbnail_size=[
            200, 400], can_get_full_size_link=True, can_create_expiring_link=False)
        self.premium_user = User.objects.create(
            username='PremiumUser', password='123', tier=self.premium)
        small_img = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.enterprise = UserTier.objects.create(tier='Enterprise', allowed_thumbnail_size=[
            200, 400], can_get_full_size_link=True, can_create_expiring_link=True)
        self.enterprise_user = User.objects.create(
            username='EnterpriseUser', password='123', tier=self.enterprise)
        self.image = SimpleUploadedFile(
            'small.png', small_img, content_type='image/png')

    def test_create_expiring_link_not_logged(self):
        self.client.post(reverse('ImageView'), data={'image': self.image})
        response = self.client.post(reverse('GenerateExpiringLink'),
                                    data={'expiration_time': 300, 'image_id': 1})
        self.assertEqual(response.status_code, 403)

    def test_create_expiring_link_basic_user(self):
        self.client.force_login(self.basic_user)
        self.client.post(reverse('ImageView'), data={'image': self.image})
        response = self.client.post(reverse('GenerateExpiringLink'),
                                    data={'expiration_time': 300, 'image_id': 1})
        self.assertEqual(response.status_code, 403)

    def test_create_expiring_link_enterprise_user(self):
        self.client.force_login(self.enterprise_user)
        self.client.post(reverse('ImageView'), data={'image': self.image})
        response = self.client.post(reverse('GenerateExpiringLink'),
                                    data={'expiration_time': 300, 'image_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)

    def test_create_expiring_link_not_existing_image(self):
        self.client.force_login(self.enterprise_user)
        self.client.post(reverse('ImageView'), data={'image': self.image})
        response = self.client.post(reverse('GenerateExpiringLink'),
                                    data={'expiration_time': 300, 'image_id': 2})
        self.assertEqual(response.status_code, 400)

    def test_create_expiring_link_wrong_expiration_time(self):
        self.client.force_login(self.enterprise_user)
        self.client.post(reverse('ImageView'), data={'image': self.image})
        response = self.client.post(reverse('GenerateExpiringLink'),
                                    data={'expiration_time': 100, 'image_id': 1})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse('GenerateExpiringLink'),
                                    data={'expiration_time': 300000000, 'image_id': 1})
        self.assertEqual(response.status_code, 400)


class ExpiringLinksViewTestCase(TestCase):
    def setUp(self):
        small_img = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.enterprise = UserTier.objects.create(tier='Enterprise', allowed_thumbnail_size=[
            200, 400], can_get_full_size_link=True, can_create_expiring_link=True)
        self.enterprise_user = User.objects.create(
            username='EnterpriseUser', password='123', tier=self.enterprise)
        self.image = SimpleUploadedFile(
            'small.png', small_img, content_type='image/png')
        self.client.force_login(self.enterprise_user)
        self.client.post(reverse('ImageView'), data={'image': self.image})
        self.expiring_link = self.client.post(reverse('GenerateExpiringLink'),
                                              data={'expiration_time': 300, 'image_id': 1}).data

    def test_get_expiring_image(self):
        get_response = self.client.get(
            reverse('ExpiringLinkView', kwargs={'signed_value': self.expiring_link.split('/')[2]}))
        self.assertEqual(get_response.status_code, 302)

    def test_get_invalid_link(self):
        get_response = self.client.get(
            reverse('ExpiringLinkView', kwargs={'signed_value': '1'}))
        self.assertEqual(get_response.status_code, 404)

    def test_get_expired_image(self):
        signer = Signer()
        expiration = int(time()) - 10000
        signed_value = signer.sign(str(1) + '|' + str(expiration))
        get_response = self.client.get(
            reverse('ExpiringLinkView', kwargs={'signed_value': signed_value}))
        self.assertEqual(get_response.status_code, 410)
