# 💡 Lógica de negocio para la app de Planos
# Modelo actual (obligatorio): titulo, descripcion, subido_por, area, subarea

from collections import Counter
from typing import List, Dict, Tuple

REGLAS = {
    "criticas": ("incendio", "colapso", "riesgo"),
    "altas": ("urgente", "fallo", "parada"),
    "prohibidas": ("xxx", "spam", "tóxico", "toxico")
}


def verificar_titulo_valido(titulo: str) -> bool:
    """
    1. Verificar si el título del plano es válido
    ---------------------------------------------
    Reglas mínimas:
    - No vacío ni solo espacios.
    - Al menos 5 caracteres.

    Ejemplos:
      verificar_titulo_valido("  ")          → False
      verificar_titulo_valido("ABC")         → False
      verificar_titulo_valido("Plano A")     → True
    """
    if not titulo:
        return False
    return len(titulo.strip()) >= 5


def contar_planos_por_usuario(planos: List[Dict], id_usuario: int) -> int:
    """
    2. Contar planos por usuario
    -----------------------------
    - planos: lista de dicts con clave 'subido_por' (int)
    - id_usuario: id del usuario

    Ejemplo:
      planos = [{"subido_por": 1}, {"subido_por": 2}, {"subido_por": 1}]
      contar_planos_por_usuario(planos, 1) → 2
    """
    return sum(1 for p in planos if p.get("subido_por") == id_usuario)


def clasificar_planos(planos: List[Dict]) -> List[Dict]:
    """
    3. Clasificar planos por tipo
    -----------------------------
    Clasifica según la 'descripcion' (y como respaldo, según 'area'):
      - 'eléctrico'/'electrico'     → 'Eléctrico'
      - 'arquitectónico'/'arquitectonico' → 'Arquitectónico'
      - 'estructural'               → 'Estructural'
      - otro                        → 'General'

    Ejemplo:
      clasificar_planos([
        {"titulo": "T1", "descripcion": "plano eléctrico", "area": "Producción"},
        {"titulo": "T2", "descripcion": "refuerzo", "area": "Arquitectónico"}
      ])
      → [{"titulo": "T1", "tipo": "Eléctrico"}, {"titulo": "T2", "tipo": "Arquitectónico"}]
    """
    clasificados = []
    for p in planos:
        desc = (p.get("descripcion") or "").strip().lower()
        area_txt = (p.get("area") or "").strip().lower()

        if ("eléctrico" in desc or "electrico" in desc or
                "eléctrico" in area_txt or "electrico" in area_txt):
            tipo = "Eléctrico"
        elif ("arquitectónico" in desc or "arquitectonico" in desc or
              "arquitectónico" in area_txt or "arquitectonico" in area_txt):
            tipo = "Arquitectónico"
        elif "estructural" in desc or "estructural" in area_txt:
            tipo = "Estructural"
        else:
            tipo = "General"

        clasificados.append({"titulo": p.get("titulo"), "tipo": tipo})

    return clasificados


def validar_plano_data(data: Dict, min_desc: int = 10) -> Tuple[bool, List[str]]:
    """
    ✅ 4. Validar datos del plano (con área y subárea OBLIGATORIAS)
    ----------------------------------------------------------------
    Reglas:
      - 'titulo': mínimo 3 caracteres y no solo números.
      - 'descripcion': si viene, mínimo `min_desc` caracteres.
      - 'area': obligatorio, mínimo 3 caracteres.
      - 'subarea': obligatorio, mínimo 3 caracteres.
      - Palabras prohibidas: 'xxx', 'spam', 'tóxico/toxico'.

    Ejemplos:
      validar_plano_data({
        "titulo": "Plano A", "descripcion": "detalle correcto",
        "area": "Producción", "subarea": "Laminado"
      }) → (True, [])

      validar_plano_data({
        "titulo": "12", "descripcion": "corta",
        "area": "", "subarea": ""
      })
      → (False, [
           "El título no puede ser solo números.",
           "La descripción es demasiado corta (mínimo 10 caracteres).",
           "El campo área es obligatorio.",
           "El campo subárea es obligatorio."
         ])
    """
    errores: List[str] = []

    titulo = (data.get("titulo") or "").strip()
    descripcion = (data.get("descripcion") or "").strip()
    area = (data.get("area") or "").strip()
    subarea = (data.get("subarea") or "").strip()

    # Título
    if len(titulo) < 3:
        errores.append("El título debe tener al menos 3 caracteres.")
    if titulo.isdigit():
        errores.append("El título no puede ser solo números.")

    # Descripción (si viene)
    if descripcion and len(descripcion) < min_desc:
        errores.append(
            f"La descripción es demasiado corta (mínimo {min_desc} caracteres).")

    # Contenido prohibido
    tit_low, desc_low = titulo.lower(), descripcion.lower()
    if any(p in tit_low or p in desc_low for p in REGLAS["prohibidas"]):
        errores.append("El contenido incluye palabras no permitidas.")

    # Área y subárea (OBLIGATORIAS con tu modelo actual)
    if not area:
        errores.append("El campo área es obligatorio.")
    elif len(area) < 3:
        errores.append("El campo área debe tener al menos 3 caracteres.")

    if not subarea:
        errores.append("El campo subárea es obligatorio.")
    elif len(subarea) < 3:
        errores.append("El campo subárea debe tener al menos 3 caracteres.")

    return (len(errores) == 0, errores)


def generar_codigo_plano(titulo: str, correlativo: int) -> str:
    """
    🧠 5. Generar código de plano
    ------------------------------
    Formato: ABC-0001 (usa las 3 primeras letras alfabéticas del título)

    Ejemplos:
      generar_codigo_plano("Plano Eléctrico", 7)  → "PLA-0007"
      generar_codigo_plano("  123 ? ", 12)        → "PLN-0012"
    """
    import re
    base = re.sub(r"[^a-zA-Z]", "", titulo).upper()[:3] or "PLN"
    return f"{base}-{correlativo:04d}"


def prioridad_plano(descripcion: str) -> int:
    """
    6. Calcular prioridad del plano según su descripción
    ----------------------------------------------------
    Palabras clave:
      3 = crítico:  'incendio', 'colapso', 'riesgo'
      2 = alto:     'urgente', 'fallo', 'parada'
      1 = normal

    Ejemplos:
      prioridad_plano("Riesgo de incendio en tablero") → 3
      prioridad_plano("Parada programada de línea")     → 2
      prioridad_plano("Plano general de layout")        → 1
    """
    d = (descripcion or "").lower()
    if any(w in d for w in REGLAS["criticas"]):
        return 3
    if any(w in d for w in REGLAS["altas"]):
        return 2
    return 1


def resumen_por_usuario(planos: List[Dict]) -> Dict[int, Dict[str, int]]:
    """
    📊 7. Resumen de planos por usuario (por tipo)
    ----------------------------------------------
    Agrupa por categorías derivadas de la descripción:
      'Eléctrico', 'Arquitectónico', 'Estructural', 'General'

    Ejemplo:
      resumen_por_usuario([
        {"subido_por": 1, "descripcion": "plano eléctrico de tablero"},
        {"subido_por": 1, "descripcion": "diseño arquitectónico"},
        {"subido_por": 2, "descripcion": "refuerzo estructural de vigas"}
      ])
      → {1: {"Eléctrico": 1, "Arquitectónico": 1}, 2: {"Estructural": 1}}
    """
    res: Dict[int, Counter] = {}
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


def resumen_por_usuario_por_area(planos: List[Dict]) -> Dict[int, Dict[str, int]]:
    """
    📊 7.1 Resumen por usuario agrupando por Área · Subárea
    -------------------------------------------------------
    Útil para ver la carga por zonas funcionales.

    Ejemplo:
      resumen_por_usuario_por_area([
        {"subido_por": 1, "area": "Producción", "subarea": "Laminado en frío"},
        {"subido_por": 1, "area": "Producción", "subarea": "Corte"},
        {"subido_por": 2, "area": "Mantenimiento", "subarea": "General"}
      ])
      → {1: {"Producción · Laminado En Frío": 1, "Producción · Corte": 1},
         2: {"Mantenimiento · General": 1}}
    """
    res: Dict[int, Counter] = {}
    for p in planos:
        uid = int(p.get("subido_por", 0))
        area = (p.get("area") or "").strip().title()
        sub = (p.get("subarea") or "").strip().title()
        # Dado que son obligatorias en el modelo, deberían venir siempre llenas.
        # Aún así, normalizamos por si llega un string vacío por error.
        area = area or "Área"
        sub = sub or "Subárea"
        clave = f"{area} · {sub}"

        res.setdefault(uid, Counter())
        res[uid][clave] += 1

    return {uid: dict(cnt) for uid, cnt in res.items()}


def detectar_duplicados(planos: List[Dict], considerar_area_subarea: bool = True) -> List[Tuple[int, int]]:
    """
    🔍 8. Detección de planos duplicados
    ------------------------------------
    Detecta registros repetidos normalizando campos (lower + strip).

    Criterio por defecto (modelo actual):
      - Misma combinación de: (titulo, descripcion, area, subarea)

    Si `considerar_area_subarea=False`, compara solo (titulo, descripcion).

    Ejemplos:
      detectar_duplicados([
        {"titulo": "Plano A", "descripcion": "instalaciones", "area": "Prod", "subarea": "Laminado"},
        {"titulo": "plano a ", "descripcion": "instalaciones ", "area": "Prod", "subarea": "Laminado"}
      ])
      → [(0, 1)]

      detectar_duplicados([
        {"titulo": "Plano A", "descripcion": "instalaciones", "area": "Prod", "subarea": "Laminado"},
        {"titulo": "plano a ", "descripcion": "instalaciones ", "area": "Mantenimiento", "subarea": "General"}
      ], considerar_area_subarea=True)
      → []   # mismo título+desc pero distinta área/subárea
    """
    vistos: Dict[Tuple[str, str, str, str], int] = {}
    duplicados: List[Tuple[int, int]] = []

    for i, p in enumerate(planos):
        t = (p.get("titulo") or "").strip().lower()
        d = (p.get("descripcion") or "").strip().lower()

        if considerar_area_subarea:
            a = (p.get("area") or "").strip().lower()
            s = (p.get("subarea") or "").strip().lower()
            clave = (t, d, a, s)
        else:
            clave = (t, d, "", "")

        if clave in vistos:
            duplicados.append((vistos[clave], i))
        else:
            vistos[clave] = i

    return duplicados
