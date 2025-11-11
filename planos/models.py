from django.db import models
from django.contrib.auth.models import User

# Este representará los planos que suben los usuarios a tu sistema.
# titulo: nombre del plano.
# descripcion: texto explicando qué es.
# fecha_subida: se guarda automáticamente la fecha al crearlo.
# subido_por: quién subió el plano (usuario que lo creó).
# str: define cómo se mostrará en el panel (por su título).


class Plano(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.CharField(max_length=100)
    subarea = models.CharField(max_length=100)

    def __str__(self):
        return self.titulo
