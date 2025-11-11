from .models import Plano
from .serializers import PlanoSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.http import Http404
from django.db.models import ProtectedError
from django.db import IntegrityError, OperationalError
import time


class PlanoViewSet(viewsets.ModelViewSet):
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer

    @action(detail=False, methods=['delete'], url_path='limpiar-pruebas')
    def limpiar_pruebas(self, request):
        """
        Endpoint optimizado para eliminar todos los planos de prueba.
        Usado por Locust al finalizar las pruebas de carga.
        URL: DELETE /api/planos/limpiar-pruebas/
        """
        max_retries = 5
        total_eliminados = 0

        for attempt in range(max_retries):
            try:
                # Obtener conteo antes de eliminar
                count = Plano.objects.count()

                if count == 0:
                    return Response(
                        {
                            "mensaje": "No hay planos para eliminar",
                            "eliminados": 0,
                            "timestamp": time.time()
                        },
                        status=status.HTTP_200_OK
                    )

                # Eliminar todos los planos
                cantidad, detalles = Plano.objects.all().delete()
                total_eliminados = cantidad

                return Response(
                    {
                        "mensaje": f"✅ Limpieza completada exitosamente",
                        "eliminados": total_eliminados,
                        "detalles": detalles,
                        "intentos": attempt + 1,
                        "timestamp": time.time()
                    },
                    status=status.HTTP_200_OK
                )

            except OperationalError as e:
                if "database is locked" in str(e).lower():
                    if attempt < max_retries - 1:
                        # Backoff exponencial más agresivo
                        # 0.5, 1, 2, 4, 8 segundos
                        wait_time = 0.5 * (2 ** attempt)
                        print(
                            f"⚠️  DB bloqueada, reintento {attempt + 1}/{max_retries} en {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        return Response(
                            {
                                "error": "Base de datos ocupada después de múltiples reintentos",
                                "eliminados": total_eliminados,
                                "intentos": max_retries,
                                "sugerencia": "Intenta de nuevo en unos segundos"
                            },
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )
                # Otro tipo de OperationalError
                return Response(
                    {"error": f"Error de operación: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except Exception as e:
                return Response(
                    {
                        "error": f"Error inesperado: {str(e)}",
                        "tipo": type(e).__name__
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Esto no debería alcanzarse
        return Response(
            {"error": "Falló después de todos los reintentos"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=False, methods=['delete'], url_path='eliminar_todos')
    def eliminar_todos(self, request):
        """Elimina todos los planos con reintentos en caso de lock"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                cantidad, _ = Plano.objects.all().delete()
                return Response(
                    {"mensaje": f"Se eliminaron {cantidad} planos."},
                    status=status.HTTP_200_OK
                )
            except OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))  # Backoff exponencial
                    continue
                return Response(
                    {"detail": "La base de datos está ocupada. Intenta de nuevo."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

    def destroy(self, request, *args, **kwargs):
        """Elimina un plano con manejo de errores y reintentos"""
        # Verificar si el objeto existe
        try:
            instance = self.get_object()
        except Http404:
            return Response(
                {"detail": "El plano no existe o ya fue eliminado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Intentar eliminar con reintentos en caso de lock
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)

            except OperationalError as e:
                # Si la base de datos está bloqueada, reintentar
                if "database is locked" in str(e):
                    if attempt < max_retries - 1:
                        # Espera con backoff exponencial
                        time.sleep(0.3 * (attempt + 1))
                        continue
                    else:
                        # Si ya agotamos reintentos, devolver error
                        return Response(
                            {"detail": "La base de datos está ocupada. Intenta de nuevo en unos segundos."},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )
                # Si es otro tipo de OperationalError, lanzarlo
                raise

            except ProtectedError:
                return Response(
                    {"detail": "No se puede eliminar: el plano está referenciado por otros registros."},
                    status=status.HTTP_409_CONFLICT
                )
            except IntegrityError:
                return Response(
                    {"detail": "No se puede eliminar por una restricción de integridad."},
                    status=status.HTTP_409_CONFLICT
                )

        # Esto no debería alcanzarse, pero por seguridad
        return Response(
            {"detail": "Error inesperado al eliminar."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
