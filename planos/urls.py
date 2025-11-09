from rest_framework.routers import DefaultRouter
from .views import PlanoViewSet

router = DefaultRouter()
router.register(r'planos', PlanoViewSet, basename='plano')

urlpatterns = router.urls
