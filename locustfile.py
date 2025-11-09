from locust import HttpUser, task, between, SequentialTaskSet
import random

API_LIST = "/api/planos/"
API_DETAIL = "/api/planos/{id}/"
# Si implementaste el endpoint para borrar todo:
API_DELETE_ALL = "/api/planos/eliminar_todos/"

# Datos de ejemplo
TITULOS = [
    "Plano de Tuberías - Área 1",
    "Plano Eléctrico - Tablero A",
    "Plano Estructural - Vigas",
    "Plano Arquitectónico - Oficinas",
]
DESCS = [
    "Distribución de tuberías para la nave principal.",
    "Circuitos y protecciones del Tablero A.",
    "Detalle de armado de vigas principales.",
    "Ambientes y accesos en zona de oficinas.",
]


class CrudPlanos(SequentialTaskSet):
    """
    Flujo secuencial para:
    - GET lista
    - POST crear
    - GET detalle
    - PUT/PATCH actualizar
    - DELETE eliminar
    Guarda el id creado para usarlo en los pasos siguientes.
    """
    created_id = None

    def on_start(self):
        # Siempre arranca con un GET para calentar cache/CSRf y validar disponibilidad
        self.client.get(API_LIST, name="GET /api/planos/")

    @task
    def create_plano(self):
        payload = {
            "titulo": random.choice(TITULOS),
            "descripcion": random.choice(DESCS),
            # ajusta según usuarios existentes
            "subido_por": random.choice([1, 2])
        }
        with self.client.post(API_LIST, json=payload, name="POST /api/planos/", catch_response=True) as resp:
            if resp.status_code == 201 and "id" in resp.json():
                self.created_id = resp.json()["id"]
                resp.success()
            else:
                resp.failure(f"POST fallo: {resp.status_code} {resp.text}")

    @task
    def get_detail(self):
        if not self.created_id:
            return
        self.client.get(API_DETAIL.format(id=self.created_id),
                        name="GET /api/planos/{id}/")

    @task
    def put_update(self):
        if not self.created_id:
            return
        payload = {
            "titulo": "ACTUALIZADO - PUT",
            "descripcion": "Actualizado completamente vía PUT",
            "subido_por": 1,
        }
        self.client.put(API_DETAIL.format(id=self.created_id),
                        json=payload, name="PUT /api/planos/{id}/")

    @task
    def patch_update(self):
        if not self.created_id:
            return
        payload = {"descripcion": "Actualizado parcialmente vía PATCH"}
        self.client.patch(API_DETAIL.format(id=self.created_id),
                          json=payload, name="PATCH /api/planos/{id}/")

    @task
    def delete_plano(self):
        if not self.created_id:
            return
        self.client.delete(API_DETAIL.format(
            id=self.created_id), name="DELETE /api/planos/{id}/")
        # reinicia para que este usuario siga el ciclo con otro recurso
        self.created_id = None


class WebsiteUser(HttpUser):
    """
    Usuario de carga que ejecuta el flujo CRUD anterior.
    Ajusta 'wait_time' para simular usuarios 'humanos'.
    """
    tasks = [CrudPlanos]
    wait_time = between(0.5, 2.0)  # pausa entre tareas
    host = "http://127.0.0.1:8000"
