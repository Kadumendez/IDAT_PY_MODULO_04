import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

# ============================================================
# Tests de API para Planos (DRF ModelViewSet)
# Ajustado a views.PlanoViewSet con acciones:
#   - eliminar_todos  -> nombre: "plano-eliminar-todos"
#   - limpiar-pruebas -> nombre: "plano-limpiar-pruebas"
# ============================================================


@pytest.fixture()
def client():
    return APIClient()


@pytest.fixture()
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="tester", password="secret123")


@pytest.fixture()
def payload_ok(user):
    return {
        "titulo": "Plano Eléctrico – Tablero A",
        "descripcion": "Diseño correcto del tablero general con derivaciones",
        "subido_por": user.id,    # FK escribible
        "area": "Producción",
        "subarea": "Laminado",
    }


@pytest.fixture()
def url_list():
    # router.register('planos', PlanoViewSet, basename='plano')
    return reverse("plano-list")


@pytest.fixture()
def url_eliminar_todos():
    # @action(url_path='eliminar_todos') -> "plano-eliminar-todos"
    return reverse("plano-eliminar-todos")


@pytest.fixture()
def url_limpiar_pruebas():
    # @action(url_path='limpiar-pruebas') -> "plano-limpiar-pruebas"
    return reverse("plano-limpiar-pruebas")


def url_detail(pk: int):
    return reverse("plano-detail", args=[pk])

# ------------------------------------------------------------
# 1) Crear
# ------------------------------------------------------------


@pytest.mark.django_db
def test_1_crear_plano_201(client, url_list, payload_ok):
    r = client.post(url_list, payload_ok, format="json")
    assert r.status_code == 201, f"Esperado 201, obtuve {r.status_code} con {getattr(r, 'data', r.content)}"
    data = r.json()
    for k in ("id", "titulo", "area", "subarea", "subido_por"):
        assert k in data


@pytest.mark.django_db
def test_1b_crear_plano_400_faltan_campos(client, url_list, payload_ok):
    bad = payload_ok | {"area": "", "subarea": ""}
    r = client.post(url_list, bad, format="json")
    assert r.status_code == 400

# ------------------------------------------------------------
# 2) Listar
# ------------------------------------------------------------


@pytest.mark.django_db
def test_2_listar_planos_200(client, url_list, payload_ok):
    client.post(url_list, payload_ok, format="json")
    r = client.get(url_list)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1

# ------------------------------------------------------------
# 3) Obtener por id
# ------------------------------------------------------------


@pytest.mark.django_db
def test_3_obtener_por_id_200(client, url_list, payload_ok):
    rid = client.post(url_list, payload_ok, format="json").json()["id"]
    r = client.get(url_detail(rid))
    assert r.status_code == 200
    assert r.json()["id"] == rid


@pytest.mark.django_db
def test_3b_obtener_por_id_404(client):
    r = client.get(url_detail(999999))
    assert r.status_code == 404

# ------------------------------------------------------------
# 4) Actualizar (PUT/PATCH)
# ------------------------------------------------------------


@pytest.mark.django_db
def test_4_put_actualizar_200(client, url_list, payload_ok):
    rid = client.post(url_list, payload_ok, format="json").json()["id"]
    updated = payload_ok | {
        "titulo": "Plano Arquitectónico – Oficina 2", "area": "Arquitectura"}
    r = client.put(url_detail(rid), updated, format="json")
    assert r.status_code == 200
    body = r.json()
    assert body["titulo"].startswith("Plano Arquitectónico")
    assert body["area"] == "Arquitectura"


@pytest.mark.django_db
def test_4b_patch_actualizar_parcial_200(client, url_list, payload_ok):
    rid = client.post(url_list, payload_ok, format="json").json()["id"]
    r = client.patch(url_detail(rid), {"subarea": "Corte"}, format="json")
    assert r.status_code == 200
    assert r.json()["subarea"] == "Corte"

# ------------------------------------------------------------
# 5) Eliminar (DELETE)
# ------------------------------------------------------------


@pytest.mark.django_db
def test_5_delete_204(client, url_list, payload_ok):
    rid = client.post(url_list, payload_ok, format="json").json()["id"]
    r = client.delete(url_detail(rid))
    # tu destroy devuelve 204 en éxito
    assert r.status_code in (200, 204)
    assert client.get(url_detail(rid)).status_code == 404


@pytest.mark.django_db
def test_5b_delete_404(client):
    assert client.delete(url_detail(999999)).status_code == 404

# ------------------------------------------------------------
# 6) Acciones personalizadas: eliminar_todos / limpiar-pruebas
# ------------------------------------------------------------


@pytest.mark.django_db
def test_6_eliminar_todos(client, url_list, url_eliminar_todos, payload_ok):
    client.post(url_list, payload_ok, format="json")
    client.post(url_list, payload_ok | {"titulo": "Plano B"}, format="json")
    r = client.delete(url_eliminar_todos)
    assert r.status_code in (200, 204)
    r2 = client.get(url_list)
    assert r2.status_code == 200
    assert r2.json() == []


@pytest.mark.django_db
def test_6b_limpiar_pruebas(client, url_list, url_limpiar_pruebas, payload_ok):
    client.post(url_list, payload_ok, format="json")
    client.post(url_list, payload_ok | {"titulo": "Plano C"}, format="json")
    r = client.delete(url_limpiar_pruebas)
    assert r.status_code in (200, 204)
    r2 = client.get(url_list)
    assert r2.status_code == 200
    assert r2.json() == []
