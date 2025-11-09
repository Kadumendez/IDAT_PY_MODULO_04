
# 💡 Lógica de negocio para la app de Planos

from collections import Counter


def verificar_titulo_valido(titulo: str) -> bool:
    """
    1. Verificar si el título del plano es válido
    ---------------------------------------------
    Verifica si el título del plano cumple con las reglas mínimas:
    - Debe tener al menos 5 caracteres.
    - No puede estar vacío o contener solo espacios.
    """
    if not titulo or len(titulo.strip()) < 5:
        return False
    return True


def contar_planos_por_usuario(planos, id_usuario: int) -> int:
    """
    2. Contar planos por usuario
    -----------------------------
    Cuenta cuántos planos pertenecen a un usuario específico.
    - planos: lista de diccionarios (cada uno con 'subido_por')
    - id_usuario: id del usuario a evaluar
        Ejemplo:
            planos = [{"subido_por": 1}, {"subido_por": 2}, {"subido_por": 1}]
            contar_planos_por_usuario(planos, 1) → 2
    """
    cantidad = 0
    for plano in planos:
        if plano.get("subido_por") == id_usuario:
            cantidad += 1
    return cantidad


def clasificar_planos(planos):
    """
    3. Clasificar planos por tipo
    -----------------------------
    Clasifica planos según su descripción.
    - Si contiene 'eléctrico' → 'Eléctrico'
    - Si contiene 'arquitectónico' → 'Arquitectónico'
    - Si contiene 'estructural' → 'Estructural'
    - Si no contiene nada de lo anterior → 'General'
    """
    clasificados = []
    for plano in planos:
        descripcion = (plano.get("descripcion") or "").strip().lower()

        if "eléctrico" in descripcion:
            tipo = "Eléctrico"
        elif "arquitectónico" in descripcion:
            tipo = "Arquitectónico"
        elif "estructural" in descripcion:
            tipo = "Estructural"
        else:
            tipo = "General"

        clasificados.append({
            "titulo": plano.get("titulo"),
            "tipo": tipo
        })

    return clasificados


def validar_plano_data(data: dict) -> tuple[bool, list[str]]:
    """
    ✅ 4. Validar los datos generales del plano
    --------------------------------------------
    Ejemplo:
        validar_plano_data({"titulo": "A", "descripcion": "plano simple"})
        → (False, ["El título debe tener al menos 3 caracteres."])
    Revisa que los datos de un plano cumplan con reglas básicas:
    - Título no vacío ni solo números.
    - Descripción mínima recomendada.
    - Sin palabras ofensivas.
    """
    errores = []
    titulo = (data.get("titulo") or "").strip().lower()
    descripcion = (data.get("descripcion") or "").strip().lower()

    if len(titulo) < 3:
        errores.append("El título debe tener al menos 3 caracteres.")
    if titulo.isdigit():
        errores.append("El título no puede ser solo números.")
    if descripcion and len(descripcion) < 10:
        errores.append(
            "La descripción es demasiado corta (mínimo 10 caracteres).")

    prohibidas = ["xxx", "spam", "tóxico"]
    if any(p in titulo or p in descripcion for p in prohibidas):
        errores.append("El contenido incluye palabras no permitidas.")

    return (len(errores) == 0, errores)


def generar_codigo_plano(titulo: str, correlativo: int) -> str:
    """
    🧠 5. Generar código de plano
    ------------------------------
    Ejemplo:
    generar_codigo_plano("Plano Eléctrico", 7) → "PLA-0007"
    Crea un código automático del formato ABC-0001 a partir del título.
    """
    import re
    base = re.sub(r"[^a-zA-Z]", "", titulo).upper()[:3] or "PLN"
    return f"{base}-{correlativo:04d}"


def prioridad_plano(descripcion: str) -> int:
    """
    6. Calcular prioridad del plano según su descripción
    ----------------------------------------------------
    Ejemplo:
        prioridad_plano("Plano crítico por riesgo de incendio") → 3
    Determina prioridad basada en palabras clave:
        3 = crítico ('incendio', 'colapso', 'riesgo')
        2 = alto ('urgente', 'fallo', 'parada')
        1 = normal
    """
    d = (descripcion or "").lower()
    if any(w in d for w in ["incendio", "colapso", "riesgo"]):
        return 3
    if any(w in d for w in ["urgente", "fallo", "parada"]):
        return 2
    return 1


def resumen_por_usuario(planos: list[dict]) -> dict[int, dict[str, int]]:
    """
    📊 7. Resumen de planos por usuario
    -----------------------------------
    Esta función agrupa y cuenta los planos de cada usuario según su tipo.
    Es útil para generar reportes o estadísticas internas.

    Ejemplo:
        resumen_por_usuario([
            {"subido_por": 1, "descripcion": "plano eléctrico de tablero"},
            {"subido_por": 1, "descripcion": "diseño arquitectónico de oficinas"},
            {"subido_por": 2, "descripcion": "refuerzo estructural de vigas"}
        ])
        ➜ {1: {"Eléctrico": 1, "Arquitectónico": 1}, 2: {"Estructural": 1}}

    Recorre una lista de planos y devuelve un resumen de cuántos planos tiene cada usuario por categoría.
    Retorna un diccionario con esta estructura:
        { user_id: {"Eléctrico": n, "Arquitectónico": n, ...}, ... }
    """
    res: dict[int, Counter] = {}
    for p in planos:
        uid = int(p.get("subido_por", 0))
        desc = (p.get("descripcion") or "").lower()

        if "eléctrico" in desc or "electrico" in desc:
            cat = "Eléctrico"
        elif "arquitectónico" in desc or "arquitectonico" in desc:
            cat = "Arquitectónico"
        elif "estructural" in desc:
            cat = "Estructural"
        else:
            cat = "General"

        res.setdefault(uid, Counter())
        res[uid][cat] += 1

    return {uid: dict(cnt) for uid, cnt in res.items()}


def detectar_duplicados(planos: list[dict]) -> list[tuple[int, int]]:
    """
    🔍 8. Detección de planos duplicados
    ------------------------------------
    Esta función compara todos los planos y detecta si existen registros repetidos
    según su título y descripción (ignorando mayúsculas y espacios).

    Ejemplo:
        detectar_duplicados([
            {"titulo": "Plano A", "descripcion": "Instalaciones eléctricas"},
            {"titulo": "plano a ", "descripcion": "instalaciones eléctricas "}
        ])
        ➜ [(0, 1)]  # Significa que el plano 0 y el plano 1 son duplicados

    Detecta posibles duplicados basándose en título y descripción normalizados.
    Retorna una lista de tuplas con los índices de los planos que se repiten.
    Ejemplo de salida: [(0, 2), (1, 3)]
    """
    vistos: dict[tuple[str, str], int] = {}
    duplicados: list[tuple[int, int]] = []

    for i, p in enumerate(planos):
        t = (p.get("titulo") or "").strip().lower()
        d = (p.get("descripcion") or "").strip().lower()
        clave = (t, d)

        if clave in vistos:
            duplicados.append((vistos[clave], i))
        else:
            vistos[clave] = i

    return duplicados
