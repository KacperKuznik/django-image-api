from django.urls import path

from .views import *

urlpatterns = [
    path('images', ImageView.as_view(), name='ImageView'),
    path('expiring-link/<str:signed_value>/',
         ExpiringLinkView.as_view(), name='ExpiringLinkView'),
    path('generate-expiring-link',
         GenerateExpiringLink.as_view(), name='GenerateExpiringLink'),
]
