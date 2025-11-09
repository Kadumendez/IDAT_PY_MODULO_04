from django.db import models
from django.contrib.auth.models import User
import unicodedata
import re


# ---------- utilidades ----------
def abreviatura_3(s: str) -> str:
    """
    Genera abreviatura de 3 letras a partir del nombre:
    - Quita tildes y caracteres no alfabéticos.
    - Convierte a mayúsculas.
    - Rellena con 'X' si queda corto.
    """
    if not s:
        return "XXX"
    # quitar tildes
    s = "".join(c for c in unicodedata.normalize(
        "NFD", s) if unicodedata.category(c) != "Mn")
    # solo letras
    s = re.sub(r"[^A-Za-z]", "", s).upper()
    base = (s[:3] or "XXX")
    return base.ljust(3, "X")


# ---------- catálogos ----------
class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    abrev = models.CharField(max_length=3, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.abrev:
            self.abrev = abreviatura_3(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.abrev})"


class Subarea(models.Model):
    area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="subareas")
    nombre = models.CharField(max_length=100)
    abrev = models.CharField(max_length=3, editable=False)

    class Meta:
        # 🔒 Evita subáreas duplicadas dentro de la MISMA área
        constraints = [
            models.UniqueConstraint(
                fields=["area", "nombre"], name="uniq_subarea_por_area")
        ]

    def save(self, *args, **kwargs):
        if not self.abrev:
            self.abrev = abreviatura_3(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.area.abrev}-{self.nombre} ({self.abrev})"


# ---------- entidad principal ----------
class Plano(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(User, on_delete=models.CASCADE)
    subarea = models.ForeignKey(
        Subarea, on_delete=models.PROTECT, related_name="planos")
    version = models.PositiveIntegerField(default=0)
    codigo = models.CharField(max_length=40, unique=True, editable=False)

    class Meta:
        # 🔒 Evita duplicar el MISMO título en la MISMA subárea y MISMA versión
        constraints = [
            models.UniqueConstraint(
                fields=["subarea", "titulo", "version"], name="uniq_plano_por_subarea_y_version")
        ]

    def __str__(self):
        return f"{self.codigo} · {self.titulo}"

    def save(self, *args, **kwargs):
        # Genera código único solo si no existe aún
        if not self.codigo and self.subarea_id:
            pref = f"{self.subarea.area.abrev}-{self.subarea.abrev}-{abreviatura_3(self.titulo)}-V{self.version:03d}-"
            # buscar el último correlativo de 4 dígitos para ese prefijo
            ultimo = (Plano.objects
                      .filter(codigo__startswith=pref)
                      .order_by("-codigo")
                      .values_list("codigo", flat=True)
                      .first())
            n = int(ultimo[-4:]) + 1 if ultimo else 1
            self.codigo = f"{pref}{n:04d}"
        super().save(*args, **kwargs)
