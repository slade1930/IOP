from rest_framework import serializers
from .models import (
    ProblemaSimplex,
    FalsaPosicion,
    GaussEliminacion,
    GaussJordan,
    DiferenciacionFinita,
    InterpolacionNewton,
)


class SimplexSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemaSimplex
        fields = "__all__"
        read_only_fields = [
            "variables_holgura",
            "tabla_inicial",
            "tabla_final",
            "solucion",
            "grafico_base64",
            "creado",
        ]

    def to_representation(self, instance):
        """Transforma los datos para la respuesta API"""
        representation = super().to_representation(instance)

        # Formatea campos complejos si existen
        if instance.tabla_inicial:
            representation["tabla_inicial"] = instance.tabla_inicial
        if instance.tabla_final:
            representation["tabla_final"] = instance.tabla_final

        return representation


class FalsaPosicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FalsaPosicion
        fields = "__all__"


class GaussEliminacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaussEliminacion
        fields = "__all__"


class GaussJordanSerializer(serializers.ModelSerializer):
    class Meta:
        model = GaussJordan
        fields = "__all__"


class DiferenciacionFinitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiferenciacionFinita
        fields = "__all__"


class InterpolacionNewtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterpolacionNewton
        fields = "__all__"
