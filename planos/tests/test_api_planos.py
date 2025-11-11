import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

# ============================================================
# 💡 Tests de API para Planos (DRF ModelViewSet)
# Basados en tus archivos:
# - models.Plano (FK subido_por -> User)
# - serializers.PlanoSerializer (fields="__all__")
# - views.PlanoViewSet con acción eliminar_todo (detail=False)
# - urls con router basename="plano"
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
        # FK escribible (tu serializer expone todos los campos)
        "subido_por": user.id,
        "area": "Producción",
        "subarea": "Laminado",
    }


@pytest.fixture()
def url_list():
    # Nombre: <basename>-list => "plano-list"
    return reverse("plano-list")


@pytest.fixture()
def url_eliminar_todo():
    # Nombre: <basename>-<url_path> => "plano-eliminar-todo"
    return reverse("plano-eliminar-todo")


def url_detail(pk: int):
    # Nombre: <basename>-detail => "plano-detail"
    return reverse("plano-detail", args=[pk])


# ------------------------------------------------------------
# 1) Crear
# ------------------------------------------------------------
@pytest.mark.django_db
def test_1_crear_plano_201(client, url_list, payload_ok):
    r = client.post(url_list, payload_ok, format="json")
    assert r.status_code == 201, f"Esperado 201, obtuve {r.status_code} con body: {getattr(r, 'data', r.content)}"
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
    created = client.post(url_list, payload_ok, format="json").json()
    rid = created["id"]
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
    created = client.post(url_list, payload_ok, format="json").json()
    rid = created["id"]
    updated = payload_ok | {
        "titulo": "Plano Arquitectónico – Oficina 2", "area": "Arquitectura"}
    r = client.put(url_detail(rid), updated, format="json")
    assert r.status_code == 200
    body = r.json()
    assert body["titulo"].startswith("Plano Arquitectónico")
    assert body["area"] == "Arquitectura"


@pytest.mark.django_db
def test_4b_patch_actualizar_parcial_200(client, url_list, payload_ok):
    created = client.post(url_list, payload_ok, format="json").json()
    rid = created["id"]
    r = client.patch(url_detail(rid), {"subarea": "Corte"}, format="json")
    assert r.status_code == 200
    assert r.json()["subarea"] == "Corte"


# ------------------------------------------------------------
# 5) Eliminar (DELETE)
# ------------------------------------------------------------
@pytest.mark.django_db
def test_5_delete_204(client, url_list, payload_ok):
    created = client.post(url_list, payload_ok, format="json").json()
    rid = created["id"]
    r = client.delete(url_detail(rid))
    assert r.status_code in (200, 204)
    r2 = client.get(url_detail(rid))
    assert r2.status_code == 404


@pytest.mark.django_db
def test_5b_delete_404(client):
    r = client.delete(url_detail(999999))
    assert r.status_code == 404


# ------------------------------------------------------------
# 6) Acción personalizada: eliminar_todo
# ------------------------------------------------------------
@pytest.mark.django_db
def test_6_eliminar_todo(client, url_list, url_eliminar_todo, payload_ok):
    # crea dos
    client.post(url_list, payload_ok, format="json")
    client.post(url_list, payload_ok | {"titulo": "Plano B"}, format="json")

    r = client.delete(url_eliminar_todo)
    assert r.status_code in (200, 204)

    # verifica que quedó vacío
    r2 = client.get(url_list)
    assert r2.status_code == 200
    assert r2.json() == []
