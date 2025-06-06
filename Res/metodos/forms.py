from django import forms
from .models import Simplex


class SimplexForm(forms.ModelForm):
    coef_objetivo = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Ingrese coeficientes separados por comas (ej: 3,5,2)",
    )

    matriz_restricciones = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        help_text="Una restricción por línea. Ejemplo: 1,2,<=,5 (para 1x₁ + 2x₂ ≤ 5)",
    )

    vector_b = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Valores separados por comas (ej: 10,15)",
    )

    desigualdades = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Se autocompletará desde las restricciones",
    )

    class Meta:
        model = Simplex
        fields = ["tipo_problema", "coef_objetivo", "matriz_restricciones", "vector_b"]

    def clean(self):
        cleaned_data = super().clean()
        # Procesamiento adicional para desigualdades
        return cleaned_data

    def clean_matriz_restricciones(self):
        data = self.cleaned_data["matriz_restricciones"]
        try:
            return [
                [float(val) for val in restriccion.split(",")[:2]]
                + [restriccion.split(",")[2]]
                for restriccion in data.split("\n")
                if restriccion.strip()
            ]
        except Exception as e:
            raise forms.ValidationError(f"Formato incorrecto. Error: {str(e)}")
