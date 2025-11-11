"""
============================================================
📈 locustfile.py – Prueba de rendimiento para la API de Planos
------------------------------------------------------------
Este archivo se usa con LOCUST para simular múltiples usuarios
interactuando con los endpoints del backend (API REST).
Incluye:
    - Creación, lectura, actualización y eliminación (CRUD).
    - Flujo secuencial de tareas.
    - Documentación detallada para cada sección.
============================================================
"""

# ------------------------------------------------------------
# 📦 Importaciones necesarias de Locust y Python estándar
# ------------------------------------------------------------
from locust import HttpUser, task, between, SequentialTaskSet
import random

# ------------------------------------------------------------
# 🌐 Endpoints base de tu API (ajusta si cambian las rutas)
# ------------------------------------------------------------
API_LIST = "/api/planos/"
API_DETAIL = "/api/planos/{id}/"
API_DELETE_ALL = "/api/planos/eliminar_todo/"

# ------------------------------------------------------------
# 🧩 Datos de ejemplo (se eligen al azar para simular variedad)
# ------------------------------------------------------------
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


"""
============================================================
🔸 CLASE: CrudPlanos (SequentialTaskSet)
------------------------------------------------------------
👉 Representa un flujo de usuario “real”, que realiza las
siguientes acciones en secuencia:

    1. GET  → lista de planos
    2. POST → crear nuevo plano
    3. GET  → obtener detalle del plano creado
    4. PUT  → actualizar completamente
    5. PATCH → actualización parcial
    6. DELETE → eliminar el plano

✅ Cada método decorado con @task representa una “tarea”
que Locust ejecutará en ese orden (secuencial).
============================================================
"""


class CrudPlanos(SequentialTaskSet):
    """
    Este conjunto de tareas CRUD usa un flujo SECUENCIAL.
    Cada usuario de carga repite este ciclo indefinidamente.
    """
    created_id = None  # Guarda el ID del plano creado

    def on_start(self):
        """
        🚀 Se ejecuta automáticamente al iniciar cada usuario.
        Sirve para verificar que la API esté disponible.
        """
        self.client.get(API_LIST, name="GET /api/planos/")

    # --------------------------------------------------------
    # 🧱 @task → FUNCIONES DE LOCUST
    # Cada @task indica una acción (petición HTTP) que
    # el usuario simulará durante la prueba.
    # --------------------------------------------------------

    @task
    def create_plano(self):
        """
        🟢 Crear un nuevo plano (POST)
        ----------------------------------------------------
        Crea un nuevo registro con datos aleatorios.
        Guarda el ID para las siguientes operaciones.
        """
        payload = {
            "titulo": random.choice(TITULOS),
            "descripcion": random.choice(DESCS),
            "subido_por": 1,  # Como tu API es pública, se puede usar 1
            "area": "Producción",
            "subarea": "Laminado",
        }

        with self.client.post(API_LIST, json=payload, name="POST /api/planos/", catch_response=True) as resp:
            if resp.status_code == 201 and "id" in resp.json():
                self.created_id = resp.json()["id"]
                resp.success()
            else:
                resp.failure(
                    f"❌ Error al crear plano ({resp.status_code}): {resp.text[:150]}")

    @task
    def get_detail(self):
        """
        🔵 Consultar el detalle de un plano (GET)
        ----------------------------------------------------
        Usa el ID almacenado en `self.created_id` del paso anterior.
        """
        if not self.created_id:
            return  # Si no hay plano creado, salta
        self.client.get(
            API_DETAIL.format(id=self.created_id),
            name="GET /api/planos/{id}/"
        )

    @task
    def put_update(self):
        """
        🟠 Actualizar completamente un plano (PUT)
        ----------------------------------------------------
        Envía todos los campos actualizados.
        """
        if not self.created_id:
            return
        payload = {
            "titulo": "ACTUALIZADO - PUT",
            "descripcion": "Actualizado completamente vía PUT",
            "subido_por": 1,
            "area": "Arquitectura",
            "subarea": "General",
        }
        self.client.put(
            API_DETAIL.format(id=self.created_id),
            json=payload,
            name="PUT /api/planos/{id}/"
        )

    @task
    def patch_update(self):
        """
        🟡 Actualizar parcialmente un plano (PATCH)
        ----------------------------------------------------
        Cambia solo un campo existente.
        """
        if not self.created_id:
            return
        payload = {"descripcion": "Actualizado parcialmente vía PATCH"}
        self.client.patch(
            API_DETAIL.format(id=self.created_id),
            json=payload,
            name="PATCH /api/planos/{id}/"
        )

    @task
    def delete_plano(self):
        """
        🔴 Eliminar un plano (DELETE)
        ----------------------------------------------------
        Borra el registro y reinicia el ciclo CRUD.
        """
        if not self.created_id:
            return
        self.client.delete(
            API_DETAIL.format(id=self.created_id),
            name="DELETE /api/planos/{id}/"
        )
        # Reinicia el ciclo
        self.created_id = None


"""
============================================================
🔸 CLASE: WebsiteUser (HttpUser)
------------------------------------------------------------
👉 Representa un “usuario virtual” que ejecuta tareas.

- Cada instancia simula una persona usando tu API.
- Usa la clase `CrudPlanos` como conjunto de tareas.
- `wait_time` define el intervalo aleatorio entre acciones.
- `host` indica la URL base de tu servidor Django/DRF.
============================================================
"""


class WebsiteUser(HttpUser):
    tasks = [CrudPlanos]         # 🔹 Asocia la clase de tareas
    wait_time = between(0.5, 2)  # 🔹 Pausa entre peticiones (en segundos)
    host = "http://127.0.0.1:8000"  # 🔹 URL base del servidor
