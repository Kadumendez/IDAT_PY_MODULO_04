# 💡 Pruebas unitarias para la lógica de Planos

from planos.services.planos_logic import (
    verificar_titulo_valido,
    contar_planos_por_usuario,
    clasificar_planos,
    validar_plano_data,
    generar_codigo_plano,
    prioridad_plano,
    resumen_por_usuario,
    detectar_duplicados,
)

"""
============================================================
🧩 1. Pruebas para la función: verificar_titulo_valido(titulo)
------------------------------------------------------------
Objetivo:
    Validar que el título de un plano cumpla las condiciones mínimas:
    - No puede ser vacío ni solo espacios.
    - Debe tener al menos 5 caracteres válidos.
Casos a probar:
    ✅ Título correcto
    🚫 Título muy corto
    🚫 Título vacío
    🚫 Título con solo espacios
============================================================
"""


def test_titulo_valido_correcto():
    """✅ Verifica que un título válido pase la prueba"""
    titulo = "Plano Eléctrico"
    assert verificar_titulo_valido(titulo) is True


def test_titulo_muy_corto():
    """🚫 Verifica que un título con menos de 5 caracteres falle"""
    titulo = "AB"
    assert verificar_titulo_valido(titulo) is False


def test_titulo_vacio():
    """🚫 Verifica que un título vacío falle"""
    titulo = ""
    assert verificar_titulo_valido(titulo) is False


def test_titulo_con_espacios():
    """🚫 Verifica que un título con solo espacios falle"""
    titulo = "    "
    assert verificar_titulo_valido(titulo) is False


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

# Dataset simple de ejemplo
PLANOS_FAKE = [
    {"titulo": "Plano Eléctrico - Tablero A",
        "descripcion": "circuitos eléctricos", "subido_por": 1},
    {"titulo": "Plano Arquitectónico - Oficinas",
        "descripcion": "diseño arquitectónico de oficinas", "subido_por": 1},
    {"titulo": "Plano Estructural - Vigas",
        "descripcion": "detalle estructural de vigas", "subido_por": 2},
    {"titulo": "Plano General - Patio",
        "descripcion": "replanteo general del patio", "subido_por": 2},
]


def test_contar_planos_por_usuario_con_id_1():
    """✅ Usuario 1 debe tener 2 planos en el dataset de prueba"""
    assert contar_planos_por_usuario(PLANOS_FAKE, 1) == 2


def test_contar_planos_por_usuario_con_id_2():
    """✅ Usuario 2 debe tener 2 planos en el dataset de prueba"""
    assert contar_planos_por_usuario(PLANOS_FAKE, 2) == 2


def test_contar_planos_por_usuario_sin_resultados():
    """✅ Usuario inexistente (id=99) debe devolver 0"""
    assert contar_planos_por_usuario(PLANOS_FAKE, 99) == 0


"""
============================================================
🧩 3. Pruebas para la función: clasificar_planos(planos)
------------------------------------------------------------
Objetivo:
    Verificar que la función asigne correctamente el tipo
    de plano según las palabras clave en la descripción.
Casos a probar:
    ✅ Cada descripción contiene un tipo conocido.
    ✅ Descripción vacía o None → 'General'
============================================================
"""


def test_clasificar_planos_devuelve_tipos_correctos():
    """✅ Debe mapear correctamente los tipos: Eléctrico, Arquitectónico, Estructural y General."""
    resultado = clasificar_planos(PLANOS_FAKE)
    m = {item["titulo"]: item["tipo"] for item in resultado}

    assert m["Plano Eléctrico - Tablero A"] == "Eléctrico"
    assert m["Plano Arquitectónico - Oficinas"] == "Arquitectónico"
    assert m["Plano Estructural - Vigas"] == "Estructural"
    assert m["Plano General - Patio"] == "General"


def test_clasificar_planos_maneja_descripcion_vacia():
    """✅ Si una descripción viene vacía o None, debe clasificarse como 'General'."""
    planos = [
        {"titulo": "Plano X", "descripcion": None, "subido_por": 1},
        {"titulo": "Plano Y", "descripcion": "", "subido_por": 1},
    ]
    res = clasificar_planos(planos)
    assert all(item["tipo"] == "General" for item in res)


"""
============================================================
🧩 4. Pruebas para la función: validar_plano_data(data)
------------------------------------------------------------
Objetivo:
    Validar los datos básicos de un plano:
    - Título no vacío ni solo números.
    - Descripción con longitud mínima.
    - Sin palabras prohibidas.
Casos a probar:
    ✅ Datos válidos
    🚫 Título demasiado corto
    🚫 Título solo numérico
    🚫 Descripción muy corta
    🚫 Palabras prohibidas
============================================================
"""


def test_validar_plano_data_valido():
    """✅ Verifica que datos correctos pasen sin errores"""
    data = {"titulo": "Plano Eléctrico",
            "descripcion": "Diseño completo de tablero eléctrico"}
    ok, errores = validar_plano_data(data)
    assert ok is True
    assert errores == []


def test_validar_plano_data_titulo_corto():
    """🚫 Título demasiado corto"""
    data = {"titulo": "A", "descripcion": "plano de sala"}
    ok, errores = validar_plano_data(data)
    assert ok is False
    assert any("al menos 3 caracteres" in e for e in errores)


def test_validar_plano_data_titulo_numerico():
    """🚫 Título formado solo por números"""
    data = {"titulo": "12345", "descripcion": "plano estructural"}
    ok, errores = validar_plano_data(data)
    assert ok is False
    assert any("números" in e for e in errores)


def test_validar_plano_data_descripcion_corta():
    """🚫 Descripción demasiado corta"""
    data = {"titulo": "Plano X", "descripcion": "corto"}
    ok, errores = validar_plano_data(data)
    assert ok is False
    assert any("demasiado corta" in e for e in errores)


def test_validar_plano_data_palabras_prohibidas():
    """🚫 Contiene palabras prohibidas"""
    data = {"titulo": "plano tóxico", "descripcion": "detalle interno"}
    ok, errores = validar_plano_data(data)
    assert ok is False
    assert any("no permitidas" in e for e in errores)


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


def test_generar_codigo_plano_normal():
    """✅ Código generado correctamente"""
    codigo = generar_codigo_plano("Plano Eléctrico", 7)
    assert codigo == "PLA-0007"


def test_generar_codigo_plano_caracteres_especiales():
    """✅ Ignora caracteres especiales y genera base correcta"""
    codigo = generar_codigo_plano("**Plano# de prueba!!", 15)
    assert codigo.startswith("PLA-") and codigo.endswith("0015")


def test_generar_codigo_plano_titulo_vacio():
    """✅ Si el título está vacío, usa 'PLN' como base"""
    codigo = generar_codigo_plano("", 1)
    assert codigo == "PLN-0001"


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


def test_prioridad_plano_critico():
    """✅ Palabras críticas deben devolver prioridad 3"""
    assert prioridad_plano("riesgo de incendio en sistema") == 3


def test_prioridad_plano_alta():
    """✅ Palabras de urgencia deben devolver prioridad 2"""
    assert prioridad_plano("fallo urgente en tablero") == 2


def test_prioridad_plano_normal():
    """✅ Descripción sin palabras clave → prioridad 1"""
    assert prioridad_plano("revisión general del plano") == 1


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


def test_resumen_por_usuario_correcto():
    """✅ Agrupa correctamente los planos por tipo y usuario"""
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


def test_resumen_por_usuario_lista_vacia():
    """✅ Si no hay planos, retorna diccionario vacío"""
    assert resumen_por_usuario([]) == {}


"""
============================================================
🧩 8. Pruebas para la función: detectar_duplicados(planos)
------------------------------------------------------------
Objetivo:
    Detectar planos con mismo título y descripción (ignorando mayúsculas y espacios).
Casos a probar:
    ✅ Duplicado simple
    ✅ Múltiples duplicados
    ✅ Sin duplicados
============================================================
"""


def test_detectar_duplicados_simple():
    """✅ Detecta un par de planos duplicados"""
    planos = [
        {"titulo": "Plano A", "descripcion": "instalaciones eléctricas"},
        {"titulo": "plano a ", "descripcion": "instalaciones eléctricas "},
    ]
    duplicados = detectar_duplicados(planos)
    assert (0, 1) in duplicados


def test_detectar_duplicados_multiples():
    """✅ Detecta múltiples pares duplicados"""
    planos = [
        {"titulo": "Plano A", "descripcion": "instalaciones eléctricas"},
        {"titulo": "Plano A", "descripcion": "instalaciones eléctricas"},
        {"titulo": "Plano B", "descripcion": "estructural"},
        {"titulo": "plano b", "descripcion": "estructural"},
    ]
    duplicados = detectar_duplicados(planos)
    assert (0, 1) in duplicados
    assert (2, 3) in duplicados


def test_detectar_duplicados_sin_coincidencias():
    """✅ No hay duplicados si los títulos y descripciones difieren"""
    planos = [
        {"titulo": "Plano A", "descripcion": "uno"},
        {"titulo": "Plano B", "descripcion": "dos"},
        {"titulo": "Plano C", "descripcion": "tres"},
    ]
    duplicados = detectar_duplicados(planos)
    assert duplicados == []
