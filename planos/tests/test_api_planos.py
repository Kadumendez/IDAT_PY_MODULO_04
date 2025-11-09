# 💡 Tests de API para el app Planos (Django REST Framework)

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from planos.models import Plano

# --------------------------------------------------------------------
# 🔧 Helpers mínimos y a prueba de cambios en el modelo
# --------------------------------------------------------------------


def _model_has_field(model, field_name: str) -> bool:
    return any(f.name == field_name for f in model._meta.get_fields())


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_auth(db):
    """Cliente autenticado con sesión (para endpoints protegidos)."""
    User = get_user_model()
    user = User.objects.create_user(username="tester", password="pass123")
    client = APIClient()
    client.login(username="tester", password="pass123")
    return client


@pytest.fixture
def fabrica_relaciones(db):
    """
    Crea las relaciones necesarias SOLO si el modelo Plano las exige.
    Devuelve un dict con kwargs válidos para crear/POSTear un Plano.
    """
    from django.apps import apps
    kwargs = {}

    # Usuario (subido_por)
    if _model_has_field(Plano, "subido_por"):
        User = get_user_model()
        uploader = User.objects.create_user(
            username="uploader", password="pass123")
        kwargs["subido_por"] = uploader.id  # Para payloads API usaremos el ID

    # Área/Subárea
    if _model_has_field(Plano, "subarea"):
        Area = apps.get_model("planos", "Area")
        Subarea = apps.get_model("planos", "Subarea")
        area = Area.objects.create(nombre="Área Demo", abrev="ARD")
        sub = Subarea.objects.create(
            nombre="Subárea Demo", abrev="SBD", area=area)
        kwargs["subarea"] = sub.id  # Para payloads API usaremos el ID

    return kwargs


def crear_plano_ORM(**extra):
    """
    Crea un Plano vía ORM, resolviendo automáticamente FKs si existen.
    - Para ORM: subido_por debe ser instancia User (no ID).
    - Para ORM: subarea debe ser instancia Subarea (ya lo hacemos).
    """
    base = dict(titulo="Plano Demo", descripcion="Descripción demo")
    from django.apps import apps
    from django.contrib.auth import get_user_model

    # ✅ User instancia (NO .pk)
    if _model_has_field(Plano, "subido_por") and "subido_por" not in extra:
        User = get_user_model()
        extra["subido_por"] = User.objects.create_user(
            username="owner", password="x")

    # ✅ Subarea instancia
    if _model_has_field(Plano, "subarea") and "subarea" not in extra:
        Area = apps.get_model("planos", "Area")
        Subarea = apps.get_model("planos", "Subarea")
        a = Area.objects.create(nombre="Área X", abrev="ARX")
        s = Subarea.objects.create(nombre="Subárea X", abrev="SBX", area=a)
        extra["subarea"] = s

    return Plano.objects.create(**base, **extra)


"""
============================================================
🧩 API 1. Listado y Detalle (GET)
------------------------------------------------------------
Objetivo:
    Verificar que los endpoints públicos de lectura respondan.
Casos a probar:
    ✅ GET /api/planos/ devuelve 200
    ✅ GET /api/planos/{id}/ devuelve 200 si existe
============================================================
"""


@pytest.mark.django_db
def test_api_listar_planos_200(api_client):
    # Aseguramos al menos 1 registro
    crear_plano_ORM()
    r = api_client.get("/api/planos/")
    assert r.status_code == 200


@pytest.mark.django_db
def test_api_detalle_plano_200(api_client):
    p = crear_plano_ORM()
    r = api_client.get(f"/api/planos/{p.id}/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("id") == p.id


"""
============================================================
🧩 API 2. Creación (POST)
------------------------------------------------------------
Objetivo:
    Validar creación de recursos y permisos.
Casos a probar:
    ✅ 201 con autenticación y payload válido
    🚫 401/403 sin autenticación
    🚫 400 si faltan campos requeridos (cuando aplique)
Notas:
    - El payload se arma dinámicamente según campos del modelo.
============================================================
"""


@pytest.mark.django_db
def test_api_crear_plano_201_autenticado(api_client_auth, fabrica_relaciones):
    payload = {"titulo": "Plano Nuevo", "descripcion": "desc"}
    # agrega subarea/subido_por si el modelo lo exige
    payload.update(fabrica_relaciones)

    r = api_client_auth.post("/api/planos/", payload, format="json")
    # DRF puede responder 200 si devuelve el mismo recurso
    assert r.status_code in (201, 200)
    assert Plano.objects.filter(titulo="Plano Nuevo").exists()


@pytest.mark.django_db
def test_api_crear_plano_401_sin_autenticacion(api_client, fabrica_relaciones):
    payload = {"titulo": "Privado", "descripcion": "x"}
    payload.update(fabrica_relaciones)

    r = api_client.post("/api/planos/", payload, format="json")
    # Según tus permisos, puede ser 401 (sin auth) o 403 (auth pero sin permisos)
    assert r.status_code in (401, 403)


"""
============================================================
🧩 API 3. Actualización (PATCH)
------------------------------------------------------------
Objetivo:
    Asegurar que el recurso se actualiza correctamente.
Casos a probar:
    ✅ 200 autenticado con datos válidos
    🚫 401/403 si no está autenticado
============================================================
"""


@pytest.mark.django_db
def test_api_actualizar_plano_200(api_client_auth):
    p = crear_plano_ORM()
    r = api_client_auth.patch(
        f"/api/planos/{p.id}/", {"descripcion": "actualizado"}, format="json")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.descripcion == "actualizado"


@pytest.mark.django_db
def test_api_actualizar_plano_401_sin_auth(api_client):
    p = crear_plano_ORM()
    r = api_client.patch(
        f"/api/planos/{p.id}/", {"descripcion": "no deberia"}, format="json")
    assert r.status_code in (401, 403)


"""
============================================================
🧩 API 4. Eliminación (DELETE)
------------------------------------------------------------
Objetivo:
    Validar borrado del recurso por ID.
Casos a probar:
    ✅ 204 autenticado
    🚫 401/403 sin autenticación
============================================================
"""


@pytest.mark.django_db
def test_api_eliminar_plano_204(api_client_auth):
    p = crear_plano_ORM()
    r = api_client_auth.delete(f"/api/planos/{p.id}/")
    assert r.status_code in (204, 200, 202)
    assert not Plano.objects.filter(id=p.id).exists()


@pytest.mark.django_db
def test_api_eliminar_plano_401_sin_auth(api_client):
    p = crear_plano_ORM()
    r = api_client.delete(f"/api/planos/{p.id}/")
    assert r.status_code in (401, 403)
