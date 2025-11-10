from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Plano
from .serializers import PlanoSerializer


class PlanoViewSet(viewsets.ModelViewSet):
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer

    # ✅ Acción personalizada para eliminar todos los registros
    @action(detail=False, methods=['delete'], url_path='eliminar_todo')
    def eliminar_todo(self, request):
        cantidad, _ = Plano.objects.all().delete()
        return Response(
            {"mensaje": f"Se eliminaron {cantidad} planos."},
            status=status.HTTP_200_OK
        )


'''
Explicación rápida:

PlanoViewSet es la vista principal que conecta el modelo y el serializer.

ModelViewSet te da automáticamente todas las funciones CRUD:

GET → Ver registros

POST → Crear

PUT → Actualizar

DELETE → Eliminar '''
