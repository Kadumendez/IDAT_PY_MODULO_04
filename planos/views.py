from rest_framework import viewsets
from .models import Plano
from .serializers import PlanoSerializer


class PlanoViewSet(viewsets.ModelViewSet):
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer


'''
Explicación rápida:

PlanoViewSet es la vista principal que conecta el modelo y el serializer.

ModelViewSet te da automáticamente todas las funciones CRUD:

GET → Ver registros

POST → Crear

PUT → Actualizar

DELETE → Eliminar '''
