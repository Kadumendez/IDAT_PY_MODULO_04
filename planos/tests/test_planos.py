# 💡 Pruebas unitarias para la lógica de Planos

from planos.services.planos_logic import (
    verificar_titulo_valido,
    contar_planos_por_usuario,
    clasificar_planos,
    validar_plano_data,
    generar_codigo_plano,
    prioridad_plano,
    resumen_por_usuario,
    resumen_por_usuario_por_area,
    detectar_duplicados,
)

import pytest

"""
============================================================
🧩 1. Pruebas para la función: verificar_titulo_valido(titulo)
------------------------------------------------------------
Objetivo:
    Verificar que el título del plano cumpla las condiciones mínimas:
    - No puede ser vacío ni solo espacios.
    - Debe tener al menos 5 caracteres válidos.
Casos a probar:
    ✅ Título correcto
    🚫 Título muy corto
    🚫 Título vacío
    🚫 Título con solo espacios
============================================================
"""


@pytest.mark.parametrize("titulo, esperado", [
    ("Plano Eléctrico", True),
    ("   Plano B   ", True),
    ("", False),
    ("   ", False),
    ("abcd", False),
    ("abcde", True),
    (None, False),
])
def test_1_verificar_titulo_valido(titulo, esperado):
    assert verificar_titulo_valido(titulo) is esperado


"""
============================================================
🧩 2. Pruebas para la función: contar_planos_por_usuario(planos, id_usuario)
------------------------------------------------------------
Objetivo:
    Comprobar que la función cuente correctamente la cantidad
    de planos pertenecientes a un usuario específico.
Casos a probar:
    ✅ Usuario con 2 planos
    ✅ Otro usuario con 2 planos
    ✅ Usuario inexistente (debe devolver 0)
============================================================
"""
PLANOS_FAKE = [
    {"titulo": "Plano Eléctrico - Tablero A",
     "descripcion": "circuitos eléctricos", "subido_por": 1, "area": "Prod", "subarea": "L1"},
    {"titulo": "Plano Arquitectónico - Oficinas",
     "descripcion": "diseño arquitectónico", "subido_por": 1, "area": "Prod", "subarea": "L2"},
    {"titulo": "Plano Estructural - Vigas",
     "descripcion": "detalle estructural", "subido_por": 2, "area": "Mant", "subarea": "Gen"},
    {"titulo": "Plano General - Patio",
     "descripcion": "replanteo general", "subido_por": 2, "area": "Mant", "subarea": "Gen"},
]


def test_2a_contar_planos_usuario_1():
    assert contar_planos_por_usuario(PLANOS_FAKE, 1) == 2


def test_2b_contar_planos_usuario_2():
    assert contar_planos_por_usuario(PLANOS_FAKE, 2) == 2


def test_2c_contar_planos_usuario_inexistente():
    assert contar_planos_por_usuario(PLANOS_FAKE, 99) == 0


"""
============================================================
🧩 3. Pruebas para la función: clasificar_planos(planos)
------------------------------------------------------------
Objetivo:
    Verificar que la función asigne correctamente el tipo
    de plano según la descripción o el área.
Casos a probar:
    ✅ Clasificación por descripción.
    ✅ Clasificación de respaldo por área.
    ✅ Insensibilidad a mayúsculas y acentos.
============================================================
"""


def test_3a_clasificar_por_descripcion():
    resultado = clasificar_planos(PLANOS_FAKE)
    m = {r["titulo"]: r["tipo"] for r in resultado}
    assert m["Plano Eléctrico - Tablero A"] == "Eléctrico"
    assert m["Plano Arquitectónico - Oficinas"] == "Arquitectónico"
    assert m["Plano Estructural - Vigas"] == "Estructural"
    assert m["Plano General - Patio"] == "General"


def test_3b_clasificar_respaldo_por_area():
    data = [
        {"titulo": "T1", "descripcion": "",
            "area": "ARQUITECTÓNICO", "subarea": "X"},
        {"titulo": "T2", "descripcion": "", "area": "electrico", "subarea": "Y"},
        {"titulo": "T3", "descripcion": "", "area": "Estructural", "subarea": "Z"},
    ]
    res = clasificar_planos(data)
    assert [r["tipo"] for r in res] == [
        "Arquitectónico", "Eléctrico", "Estructural"]


"""
============================================================
🧩 4. Pruebas para la función: validar_plano_data(data, min_desc=10)
------------------------------------------------------------
Objetivo:
    Validar los datos básicos de un plano:
    - Título no vacío ni solo números.
    - Descripción con longitud mínima.
    - Sin palabras prohibidas.
    - Área y subárea obligatorias.
Casos a probar:
    ✅ Datos válidos
    🚫 Título demasiado corto o numérico
    🚫 Descripción muy corta o prohibida
    🚫 Campos vacíos
============================================================
"""


def test_4a_validar_plano_data_valido():
    data = {
        "titulo": "Plano Eléctrico",
        "descripcion": "Diseño completo de tablero eléctrico",
        "area": "Producción",
        "subarea": "Laminado"
    }
    ok, errores = validar_plano_data(data)
    assert ok is True
    assert errores == []


@pytest.mark.parametrize("data, fragmentos", [
    ({"titulo": "A", "descripcion": "plano de sala", "area": "A", "subarea": "B"},
     ["al menos 3"]),
    ({"titulo": "12345", "descripcion": "plano estructural", "area": "Pr", "subarea": "La"},
     ["números"]),
    ({"titulo": "Plano tóxico", "descripcion": "detalle toxico", "area": "Producción", "subarea": "General"},
     ["no permitidas"]),
    ({"titulo": "Plano A", "descripcion": "corto", "area": "Producción", "subarea": "General"},
     ["demasiado corta"]),
    ({"titulo": "", "descripcion": "", "area": "", "subarea": ""},
     ["obligatorio"]),
])
def test_4b_validar_plano_data_errores(data, fragmentos):
    ok, errores = validar_plano_data(data)
    assert not ok
    joined = " | ".join(errores).lower()
    for frag in fragmentos:
        assert frag.lower().split()[0] in joined


def test_4c_validar_plano_data_min_desc_custom():
    data = {
        "titulo": "Plano B",
        "descripcion": "corta",
        "area": "Producción",
        "subarea": "L1"
    }
    ok, errores = validar_plano_data(data, min_desc=6)
    assert not ok
    assert any("mínimo 6" in e for e in errores)


"""
============================================================
🧩 5. Pruebas para la función: generar_codigo_plano(titulo, correlativo)
------------------------------------------------------------
Objetivo:
    Generar un código de plano en formato ABC-0001.
Casos a probar:
    ✅ Generación normal
    ✅ Con caracteres especiales
    ✅ Título vacío (usa PLN)
============================================================
"""


@pytest.mark.parametrize("titulo, corr, prefijo", [
    ("Plano Eléctrico", 7, "PLA-"),
    ("**Plano# de prueba!!", 15, "PLA-"),
    ("", 1, "PLN-"),
    ("A!!B??C", 9, "ABC-"),
])
def test_5_generar_codigo_plano(titulo, corr, prefijo):
    codigo = generar_codigo_plano(titulo, corr)
    assert codigo.startswith(prefijo)
    assert codigo.endswith(f"{corr:04d}")


"""
============================================================
🧩 6. Pruebas para la función: prioridad_plano(descripcion)
------------------------------------------------------------
Objetivo:
    Evaluar la prioridad según palabras clave.
Casos a probar:
    ✅ Prioridad crítica ('incendio', 'colapso', 'riesgo')
    ✅ Prioridad alta ('urgente', 'fallo', 'parada')
    ✅ Prioridad normal (sin palabras clave)
============================================================
"""


@pytest.mark.parametrize("desc, esperado", [
    ("riesgo de incendio en sistema", 3),
    ("fallo urgente en tablero", 2),
    ("revisión general del plano", 1),
    ("", 1),
    (None, 1),
])
def test_6_prioridad_plano(desc, esperado):
    assert prioridad_plano(desc) == esperado


"""
============================================================
🧩 7. Pruebas para la función: resumen_por_usuario(planos)
------------------------------------------------------------
Objetivo:
    Generar un resumen de planos agrupados por usuario y tipo.
Casos a probar:
    ✅ Usuarios con categorías distintas
    ✅ Lista vacía (resultado vacío)
============================================================
"""


def test_7a_resumen_por_usuario_correcto():
    planos = [
        {"subido_por": 1, "descripcion": "plano eléctrico general"},
        {"subido_por": 1, "descripcion": "diseño arquitectónico base"},
        {"subido_por": 2, "descripcion": "refuerzo estructural de columnas"},
        {"subido_por": 3, "descripcion": "plano general de paisajismo"},
    ]
    resultado = resumen_por_usuario(planos)
    assert resultado[1]["Eléctrico"] == 1
    assert resultado[1]["Arquitectónico"] == 1
    assert resultado[2]["Estructural"] == 1
    assert resultado[3]["General"] == 1


def test_7b_resumen_por_usuario_lista_vacia():
    assert resumen_por_usuario([]) == {}


"""
============================================================
🧩 7.1 Pruebas para la función: resumen_por_usuario_por_area(planos)
------------------------------------------------------------
Objetivo:
    Agrupar los planos por usuario considerando Área y Subárea.
Casos a probar:
    ✅ Usuarios con múltiples combinaciones de Área · Subárea.
    🚫 Valores vacíos (normaliza a 'Área · Subárea').
============================================================
"""


def test_7_1_resumen_por_usuario_por_area():
    planos = [
        {"subido_por": 1, "area": "producción", "subarea": "laminado en frío"},
        {"subido_por": 1, "area": "producción", "subarea": "corte"},
        {"subido_por": 2, "area": "mantenimiento", "subarea": "general"},
        {"subido_por": 2, "area": "", "subarea": ""},
    ]
    res = resumen_por_usuario_por_area(planos)
    assert res[1]["Producción · Laminado En Frío"] == 1
    assert res[1]["Producción · Corte"] == 1
    assert res[2]["Mantenimiento · General"] == 1
    assert res[2]["Área · Subárea"] == 1


"""
============================================================
🧩 8. Pruebas para la función: detectar_duplicados(planos)
------------------------------------------------------------
Objetivo:
    Detectar planos con mismo título y descripción (ignorando mayúsculas y espacios).
Casos a probar:
    ✅ Duplicado simple
    ✅ Sin duplicados
============================================================
"""


def test_8a_detectar_duplicados_con_area_subarea():
    planos = [
        {"titulo": "Plano A", "descripcion": "instalaciones",
            "area": "Prod", "subarea": "L1"},
        {"titulo": "plano a ", "descripcion": "instalaciones ",
            "area": "Prod", "subarea": "L1"},
        {"titulo": "Plano B", "descripcion": "instalaciones",
            "area": "Mant", "subarea": "Gen"},
    ]
    duplicados = detectar_duplicados(planos, considerar_area_subarea=True)
    assert duplicados == [(0, 1)]


def test_8b_detectar_duplicados_sin_area_subarea():
    planos = [
        {"titulo": "Plano A", "descripcion": "instalaciones",
            "area": "Prod", "subarea": "L1"},
        {"titulo": "plano a ", "descripcion": "instalaciones ",
            "area": "Mant", "subarea": "Gen"},
        {"titulo": "Otro", "descripcion": "otra cosa",
            "area": "Prod", "subarea": "L1"},
    ]
    duplicados = detectar_duplicados(planos, considerar_area_subarea=False)
    assert duplicados == [(0, 1)]


def test_8c_detectar_duplicados_lista_pequena():
    assert detectar_duplicados([]) == []
    assert detectar_duplicados(
        [{"titulo": "A", "descripcion": "B", "area": "C", "subarea": "D"}]) == []
