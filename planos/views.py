from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Plano
from .serializers import PlanoSerializer


class PlanoViewSet(ModelViewSet):
    queryset = Plano.objects.all().order_by('id')
    serializer_class = PlanoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


'''
Explicación rápida:

PlanoViewSet es la vista principal que conecta el modelo y el serializer.

ModelViewSet da automáticamente todas las funciones CRUD:

GET → Ver registros
POST → Crear
PUT → Actualizar
DELETE → Eliminar '''
