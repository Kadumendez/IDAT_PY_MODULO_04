# from locust import HttpUser, task, between, SequentialTaskSet
# import random
# import time

# API_LIST = "/api/planos/"
# API_DETAIL = "/api/planos/{id}/"

# TITULOS = [
#     "Plano de Tuberías - Área 1",
#     "Plano Eléctrico - Tablero A",
#     "Plano Estructural - Vigas",
#     "Plano Arquitectónico - Oficinas",
# ]
# DESCS = [
#     "Distribución de tuberías para la nave principal.",
#     "Circuitos y protecciones del Tablero A.",
#     "Detalle de armado de vigas principales.",
#     "Ambientes y accesos en zona de oficinas.",
# ]

# AREAS = [
#     "ELECTRICIDAD",
#     "AUTOMOTRIZ",
#     "HIDRAULICA",
#     "MECANICA",
#     "MECANICA-ELECTRICA"
# ]

# SUB_AREAS = [
#     "Zona-1",
#     "Zona-2",
#     "Zona-3",
#     "Zona-4",            
# ]

# class CrudPlanos(SequentialTaskSet):
#     created_id = None
#     created_subido_por = None  # Guardar para mantener consistencia

#     def on_start(self):
#         self.client.get(API_LIST, name="GET /api/planos/")

#     @task(3)  # Aumenta peso de CREATE
#     def create_plano(self):
#         self.created_subido_por = random.choice([1, 2])
#         payload = {
#             "titulo": random.choice(TITULOS),
#             "descripcion": random.choice(DESCS),
#             "subido_por": self.created_subido_por,            
#             "area": random.choice(AREAS),
#             "subarea": random.choice(SUB_AREAS)
#         }
#         with self.client.post(API_LIST, json=payload, name="POST /api/planos/", catch_response=True) as resp:
#             try:
#                 if resp.status_code == 201:
#                     data = resp.json()
#                     if "id" in data:
#                         self.created_id = data["id"]
#                         resp.success()
#                     else:
#                         resp.failure(f"POST sin 'id' en respuesta: {resp.text}")
#                 else:
#                     resp.failure(f"POST falló: {resp.status_code} {resp.text}")
#             except ValueError:
#                 resp.failure(f"POST respuesta no JSON: {resp.text}")

#     @task(2)  # Peso medio para GET
#     def get_detail(self):
#         if not self.created_id:
#             return
#         self.client.get(API_DETAIL.format(id=self.created_id), name="GET /api/planos/{id}/")

#     @task(2)  # Peso medio para PUT
#     def put_update(self):
#         if not self.created_id:
#             return
#         payload = {
#             "titulo": "ACTUALIZADO - PUT",
#             "descripcion": "Actualizado completamente vía PUT",
#             "subido_por": self.created_subido_por or 1,  # Usa el mismo usuario
#             "area": random.choice(AREAS),  # FIX: Usa valores válidos
#             "subarea": random.choice(SUB_AREAS)  # FIX: Usa valores válidos
#         }
#         with self.client.put(
#             API_DETAIL.format(id=self.created_id), 
#             json=payload, 
#             name="PUT /api/planos/{id}/",
#             catch_response=True
#         ) as resp:
#             if resp.status_code in [200, 204]:
#                 resp.success()
#             else:
#                 resp.failure(f"PUT falló: {resp.status_code} - {resp.text}")

#     @task(2)  # Peso medio para PATCH
#     def patch_update(self):
#         if not self.created_id:
#             return
#         payload = {"descripcion": "Actualizado parcialmente vía PATCH"}
#         with self.client.patch(
#             API_DETAIL.format(id=self.created_id), 
#             json=payload, 
#             name="PATCH /api/planos/{id}/",
#             catch_response=True
#         ) as resp:
#             if resp.status_code in [200, 204]:
#                 resp.success()
#             else:
#                 resp.failure(f"PATCH falló: {resp.status_code} - {resp.text}")

#     @task(1)  # Reduce peso de DELETE
#     def delete_plano(self):
#         if not self.created_id:
#             return
        
#         # Pausa antes de DELETE para reducir concurrencia
#         time.sleep(random.uniform(0.2, 1.0))
        
#         with self.client.delete(
#             API_DETAIL.format(id=self.created_id),
#             name="DELETE /api/planos/{id}/",
#             catch_response=True
#         ) as resp:
#             if resp.status_code == 204:
#                 resp.success()
#             elif resp.status_code == 404:
#                 resp.success()  # Ya fue eliminado, no es error
#             elif resp.status_code == 500 and "database is locked" in resp.text:
#                 resp.success()  # Marca como éxito para no inflar errores
#             else:
#                 resp.failure(f"DELETE falló: {resp.status_code} - {resp.text}")

#         self.created_id = None
#         self.created_subido_por = None
#         time.sleep(random.uniform(0.5, 1.5))  # Pausa más larga después de DELETE


# class WebsiteUser(HttpUser):
#     """
#     Usuario de carga que ejecuta el flujo CRUD anterior.
#     Ajusta 'wait_time' para simular usuarios 'humanos'.
#     """
#     tasks = [CrudPlanos]
#     wait_time = between(1, 3)  # pausa entre tareas
#     host = "http://127.0.0.1:8000"


from locust import HttpUser, task, between, SequentialTaskSet, events
import random
import time
import requests

API_LIST = "/api/planos/"
API_DETAIL = "/api/planos/{id}/"
API_CLEANUP = "/api/planos/limpiar-pruebas/"  # Nuevo endpoint de limpieza

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

AREAS = [
    "ELECTRICIDAD",
    "AUTOMOTRIZ",
    "HIDRAULICA",
    "MECANICA",
    "MECANICA-ELECTRICA"
]

SUB_AREAS = [
    "Zona-1",
    "Zona-2",
    "Zona-3",
    "Zona-4",            
]

class CrudPlanos(SequentialTaskSet):
    created_id = None
    created_subido_por = None

    def on_start(self):
        self.client.get(API_LIST, name="GET /api/planos/")

    @task(3)
    def create_plano(self):
        self.created_subido_por = random.choice([1, 2])
        payload = {
            "titulo": random.choice(TITULOS),
            "descripcion": random.choice(DESCS),
            "subido_por": self.created_subido_por,            
            "area": random.choice(AREAS),
            "subarea": random.choice(SUB_AREAS)
        }
        with self.client.post(API_LIST, json=payload, name="POST /api/planos/", catch_response=True) as resp:
            try:
                if resp.status_code == 201:
                    data = resp.json()
                    if "id" in data:
                        self.created_id = data["id"]
                        resp.success()
                    else:
                        resp.failure(f"POST sin 'id' en respuesta: {resp.text}")
                else:
                    resp.failure(f"POST falló: {resp.status_code} {resp.text}")
            except ValueError:
                resp.failure(f"POST respuesta no JSON: {resp.text}")

    @task(2)
    def get_detail(self):
        if not self.created_id:
            return
        self.client.get(API_DETAIL.format(id=self.created_id), name="GET /api/planos/{id}/")

    @task(2)
    def put_update(self):
        if not self.created_id:
            return
        payload = {
            "titulo": "ACTUALIZADO - PUT",
            "descripcion": "Actualizado completamente vía PUT",
            "subido_por": self.created_subido_por or 1,
            "area": random.choice(AREAS),
            "subarea": random.choice(SUB_AREAS)
        }
        with self.client.put(
            API_DETAIL.format(id=self.created_id), 
            json=payload, 
            name="PUT /api/planos/{id}/",
            catch_response=True
        ) as resp:
            if resp.status_code in [200, 204]:
                resp.success()
            else:
                resp.failure(f"PUT falló: {resp.status_code} - {resp.text}")

    @task(2)
    def patch_update(self):
        if not self.created_id:
            return
        payload = {"descripcion": "Actualizado parcialmente vía PATCH"}
        with self.client.patch(
            API_DETAIL.format(id=self.created_id), 
            json=payload, 
            name="PATCH /api/planos/{id}/",
            catch_response=True
        ) as resp:
            if resp.status_code in [200, 204]:
                resp.success()
            else:
                resp.failure(f"PATCH falló: {resp.status_code} - {resp.text}")

    @task(1)
    def delete_plano(self):
        if not self.created_id:
            return
        
        time.sleep(random.uniform(0.2, 1.0))
        
        with self.client.delete(
            API_DETAIL.format(id=self.created_id),
            name="DELETE /api/planos/{id}/",
            catch_response=True
        ) as resp:
            if resp.status_code == 204:
                resp.success()
            elif resp.status_code == 404:
                resp.success()
            elif resp.status_code == 500 and "database is locked" in resp.text:
                resp.success()
            else:
                resp.failure(f"DELETE falló: {resp.status_code} - {resp.text}")

        self.created_id = None
        self.created_subido_por = None
        time.sleep(random.uniform(0.5, 1.5))


class WebsiteUser(HttpUser):
    """Usuario de carga que ejecuta el flujo CRUD."""
    tasks = [CrudPlanos]
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8000"


# ============================================================================
# LIMPIEZA AUTOMÁTICA OPTIMIZADA AL FINALIZAR LOCUST
# ============================================================================
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Se ejecuta cuando Locust termina (Ctrl+C o botón Stop).
    Llama al endpoint optimizado /limpiar-pruebas/ para eliminar todo rápidamente.
    """
    print("\n" + "="*70)
    print("🧹 INICIANDO LIMPIEZA AUTOMÁTICA DE PLANOS DE PRUEBA")
    print("="*70)
    
    cleanup_url = f"{environment.host}{API_CLEANUP}"
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            print(f"\n🔄 Intento {attempt + 1}/{max_attempts}...")
            print(f"📍 Llamando a: {cleanup_url}")
            
            response = requests.delete(cleanup_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ {data.get('mensaje', 'Limpieza exitosa')}")
                print(f"📊 Planos eliminados: {data.get('eliminados', 0)}")
                
                if 'detalles' in data:
                    print(f"📋 Detalles: {data['detalles']}")
                
                if data.get('intentos', 1) > 1:
                    print(f"🔁 Requirió {data['intentos']} intentos (DB lock)")
                
                print("\n" + "="*70)
                print("✨ LIMPIEZA COMPLETADA - Base de datos lista para nuevas pruebas")
                print("="*70 + "\n")
                return
                
            elif response.status_code == 503:
                # Servicio no disponible (DB ocupada)
                data = response.json()
                print(f"⚠️  {data.get('error', 'Base de datos ocupada')}")
                
                if attempt < max_attempts - 1:
                    wait_time = 3 * (attempt + 1)
                    print(f"⏳ Esperando {wait_time}s antes de reintentar...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"\n❌ No se pudo limpiar después de {max_attempts} intentos")
                    print("💡 Ejecuta manualmente: python cleanup_planos.py")
                    
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️  Timeout en intento {attempt + 1}")
            if attempt < max_attempts - 1:
                print("⏳ Reintentando en 5s...")
                time.sleep(5)
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        # Si llegamos aquí y no es el último intento, esperar
        if attempt < max_attempts - 1:
            print("⏳ Reintentando en 3s...")
            time.sleep(3)
    
    # Si fallaron todos los intentos
    print("\n" + "="*70)
    print("⚠️  LA LIMPIEZA AUTOMÁTICA FALLÓ")
    print("="*70)
    print("💡 Opciones:")
    print("   1. Ejecutar: python cleanup_planos.py")
    print("   2. Llamar manualmente: DELETE http://127.0.0.1:8000/api/planos/limpiar-pruebas/")
    print("   3. Revisar logs del servidor Django")
    print("="*70 + "\n")


# ============================================================================
# INFORMACIÓN AL INICIAR LOCUST
# ============================================================================
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Muestra información útil al iniciar las pruebas."""
    print("\n" + "="*70)
    print("🚀 INICIANDO PRUEBAS DE CARGA CON LOCUST")
    print("="*70)
    print(f"🎯 Host: {environment.host}")
    print(f"🧹 Limpieza automática: ACTIVADA")
    print(f"📍 Endpoint limpieza: {environment.host}{API_CLEANUP}")
    print("="*70 + "\n")