from django.urls import path, include
from rest_framework import routers
from .views import PlanoViewSet

router = routers.DefaultRouter()
router.register(r'planos', PlanoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
