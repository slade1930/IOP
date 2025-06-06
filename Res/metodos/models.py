from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Simplex(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    coef_objetivo = ArrayField(
        models.FloatField(), help_text="Coeficientes de la función objetivo."
    )
    matriz_restricciones = ArrayField(
        ArrayField(models.FloatField()), help_text="Matriz de restricciones."
    )
    vector_b = ArrayField(
        models.FloatField(), help_text="Lado derecho de las restricciones."
    )
    desigualdades = ArrayField(
        models.CharField(max_length=2),
        help_text="Lista de desigualdades ('<=', '>=', '=').",
    )
    tipo_problema = models.CharField(
        max_length=3,
        choices=[("max", "Maximizar"), ("min", "Minimizar")],
        default="max",
    )
    resultado = models.JSONField(blank=True, null=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Problema Simplex {self.id}"

    class Meta:
        verbose_name = "Cálculo Simplex"
        verbose_name_plural = "Cálculos Simplex"
        ordering = ["-creado"]
