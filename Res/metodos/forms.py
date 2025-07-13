from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    ProblemaSimplex,
    FalsaPosicion,
    GaussEliminacion,
    GaussJordan,
    DiferenciacionFinita,
    InterpolacionNewton,
)
import re


class SimplexForm(forms.ModelForm):
    class Meta:
        model = ProblemaSimplex
        fields = [
            "objetivo",
            "tipo_optimizacion",
            "restricciones",
            "variables_decision",
            "tolerancia",
            "max_iteraciones",
        ]
        widgets = {
            "objetivo": forms.TextInput(
                attrs={
                    "placeholder": "Ej: 3x1 + 2x2 + 5x3",
                    "class": "function-input",
                    "pattern": r"^[0-9xX\+\-\*\/\.\s]+$",  # Corrección aquí: añadido 'r' para raw string
                    "title": "Use solo números, variables (x1, x2), y operadores básicos",
                }
            ),
            "tipo_optimizacion": forms.Select(attrs={"class": "form-control"}),
            "restricciones": forms.Textarea(
                attrs={
                    "placeholder": "Ej: 2x1 + x2 <= 20; x1 + 3x2 <= 30",
                    "rows": 3,
                    "class": "form-control",
                    "title": "Separe restricciones con punto y coma. Use <=, >= o =",
                }
            ),
            "variables_decision": forms.NumberInput(
                attrs={
                    "min": "1",
                    "max": "10",
                    "value": "2",
                    "class": "form-control",
                    "title": "Entre 1 y 10 variables",
                }
            ),
            "tolerancia": forms.NumberInput(
                attrs={
                    "step": "any",
                    "min": "0.000000001",
                    "value": "0.001",
                    "class": "form-control",
                    "title": "Valor mínimo: 0.000000001",
                }
            ),
            "max_iteraciones": forms.NumberInput(
                attrs={
                    "min": "10",
                    "max": "1000",
                    "value": "100",
                    "class": "form-control",
                    "title": "Entre 10 y 1000 iteraciones",
                }
            ),
        }
        help_texts = {
            "objetivo": "Ingrese la función objetivo usando variables como x1, x2, etc. Ej: 3x1 + 2x2 - 4x3",
            "restricciones": "Separe cada restricción con punto y coma (;). Use <=, >= o =. Ej: 2x1 + x2 <= 20; x1 - 3x2 >= 10",
            "variables_decision": "Número de variables en el problema (entre 1 y 10)",
            "tolerancia": "Valor mínimo para considerar un número como cero (≥ 1e-9)",
            "max_iteraciones": "Número máximo de iteraciones permitidas (entre 10 y 1000)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validadores adicionales para coincidir con el modelo
        self.fields["variables_decision"].validators.extend(
            [MinValueValidator(1), MaxValueValidator(10)]
        )
        self.fields["tolerancia"].validators.append(MinValueValidator(1e-9))
        self.fields["max_iteraciones"].validators.extend(
            [MinValueValidator(10), MaxValueValidator(1000)]
        )

    def clean_objetivo(self):
        objetivo = self.cleaned_data["objetivo"].strip()

        if not objetivo:
            raise forms.ValidationError("La función objetivo no puede estar vacía")

        # Validación mejorada de la función objetivo
        pattern = r"^([+-]?\d*\.?\d*[xX]\d+\s*([+-]\s*\d*\.?\d*[xX]\d+)*\s*([+-]\s*\d*\.?\d+)*\s*)$"
        if not re.fullmatch(pattern, objetivo.replace(" ", "")):
            raise forms.ValidationError(
                "Formato incorrecto. Use términos como: 3x1, -2.5x2, +x3, 10"
            )

        # Verificar que las variables sean consecutivas (x1, x2, ...)
        variables = sorted(int(m[1:]) for m in re.findall(r"[xX]\d+", objetivo))
        if variables and variables != list(range(1, max(variables) + 1)):
            raise forms.ValidationError(
                "Las variables deben ser consecutivas (x1, x2, ...) sin saltos"
            )

        return objetivo

    def clean_restricciones(self):
        restricciones = self.cleaned_data["restricciones"].strip()

        if not restricciones:
            raise forms.ValidationError("Debe ingresar al menos una restricción")

        # Validación mejorada de restricciones
        for i, restr in enumerate(filter(None, restricciones.split(";"))):
            restr = restr.strip()
            if not restr:
                continue

            # Verificar estructura básica
            if not re.match(r"^(.+)(<=|>=|=)(.+)$", restr):
                raise forms.ValidationError(
                    f"Restricción {i+1} mal formada. Use formato: [expresión] [<=|>=|=] [valor]"
                )

            # Verificar caracteres válidos
            if not re.match(r"^[\dxX\+\-\.\*/\s<=>]+$", restr):
                raise forms.ValidationError(
                    f"Restricción {i+1} contiene caracteres no permitidos"
                )

        return restricciones

    def clean(self):
        cleaned_data = super().clean()
        # Validación cruzada entre variables_decision y las usadas en las expresiones
        if "objetivo" in cleaned_data and "variables_decision" in cleaned_data:
            objetivo = cleaned_data["objetivo"]
            num_vars = cleaned_data["variables_decision"]

            # Encontrar la variable más alta usada
            variables = [int(m[1:]) for m in re.findall(r"[xX]\d+", objetivo)]
            max_var = max(variables) if variables else 0

            if max_var > num_vars:
                raise forms.ValidationError(
                    f"Usó x{max_var} pero definió solo {num_vars} variables. "
                    f"Ajuste el número de variables o las expresiones."
                )

        return cleaned_data


class FalsaPosicionForm(forms.ModelForm):
    class Meta:
        model = FalsaPosicion
        fields = ["funcion", "x0", "x1", "tolerancia", "max_iteraciones"]
        widgets = {
            "funcion": forms.TextInput(
                attrs={"placeholder": "x**3 - x - 2", "class": "function-input"}
            ),
            "x0": forms.NumberInput(attrs={"step": "any", "placeholder": "Ej. 1.0"}),
            "x1": forms.NumberInput(attrs={"step": "any", "placeholder": "Ej. 2.0"}),
            "tolerancia": forms.NumberInput(
                attrs={"step": "any", "min": "0", "value": "0.0001"}
            ),
            "max_iteraciones": forms.NumberInput(attrs={"min": "1", "value": "100"}),
        }
        help_texts = {
            "funcion": "Use x como variable. Operadores: +, -, *, /, **",
            "tolerancia": "Precisión deseada para el resultado",
        }


class GaussEliminacionForm(forms.ModelForm):
    class Meta:
        model = GaussEliminacion
        fields = ["matriz_a", "vector_b"]
        widgets = {
            "matriz_a": forms.Textarea(
                attrs={"placeholder": "[[2, 1], [5, 7]]", "rows": 4}
            ),
            "vector_b": forms.Textarea(attrs={"placeholder": "[11, 13]", "rows": 2}),
        }


class GaussJordanForm(forms.ModelForm):
    class Meta:
        model = GaussJordan
        fields = ["problema", "matriz_a", "vector_b"]
        widgets = {
            "problema": forms.Textarea(
                attrs={
                    "placeholder": "Ejemplo: Inversión en bonos municipales...",
                    "rows": 3,
                }
            ),
            "matriz_a": forms.Textarea(
                attrs={
                    "placeholder": "[[1, 1], [0.105, 0.12]] para problema de 2 inversiones",
                    "rows": 3,
                }
            ),
            "vector_b": forms.Textarea(
                attrs={
                    "placeholder": "[12000, 1335] para el ejemplo anterior",
                    "rows": 2,
                }
            ),
        }
        labels = {
            "problema": "Descripción del Problema Económico",
            "matriz_a": "Coeficientes del Sistema",
            "vector_b": "Términos Independientes",
        }


class DiferenciacionFinitaForm(forms.ModelForm):
    class Meta:
        model = DiferenciacionFinita
        fields = ["funcion", "punto", "h", "orden", "tipo"]
        widgets = {
            "funcion": forms.TextInput(
                attrs={"placeholder": "sin(x)", "class": "function-input"}
            ),
            "punto": forms.NumberInput(attrs={"step": "any", "placeholder": "Ej. 1.0"}),
            "h": forms.NumberInput(attrs={"step": "any", "value": "0.01"}),
            "orden": forms.NumberInput(attrs={"min": "1", "value": "1"}),
            "tipo": forms.Select(
                choices=[
                    ("adelante", "Diferencia Adelante"),
                    ("atras", "Diferencia Atrás"),
                    ("central", "Diferencia Central"),
                ]
            ),
        }
        help_texts = {
            "funcion": "Use x como variable. Operadores: +, -, *, /, **, sin, cos, tan, exp, log",
            "h": "Paso de aproximación para la derivada numérica",
            "orden": "Orden de la derivada que desea calcular",
            "tipo": "Tipo de fórmula de diferencias finitas",
        }

    def clean_funcion(self):
        funcion = self.cleaned_data["funcion"]
        # Validación básica de la función
        if "x" not in funcion:
            raise forms.ValidationError("La función debe contener la variable 'x'")
        return funcion


class InterpolacionNewtonForm(forms.ModelForm):
    x_vals_input = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "1, 2, 3", "rows": 2}),
        help_text="Valores de x separados por comas",
    )
    y_vals_input = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "2, 4, 6", "rows": 2}),
        help_text="Valores de y separados por comas",
    )

    class Meta:
        model = InterpolacionNewton
        fields = ["x_vals_input", "y_vals_input", "x_interpolar"]
        widgets = {
            "x_interpolar": forms.NumberInput(
                attrs={"step": "any", "placeholder": "Ej. 2.5"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        x_vals = cleaned_data.get("x_vals_input", "").strip()
        y_vals = cleaned_data.get("y_vals_input", "").strip()

        try:
            x_list = [float(x.strip()) for x in x_vals.split(",") if x.strip()]
            y_list = [float(y.strip()) for y in y_vals.split(",") if y.strip()]
        except ValueError:
            raise forms.ValidationError(
                "Los valores deben ser números separados por comas"
            )

        if len(x_list) != len(y_list):
            raise forms.ValidationError("Debe haber el mismo número de valores x e y")

        if len(x_list) < 2:
            raise forms.ValidationError(
                "Se necesitan al menos 2 puntos para interpolación"
            )

        cleaned_data["x_vals"] = x_list
        cleaned_data["y_vals"] = y_list
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.x_vals = self.cleaned_data["x_vals"]
        instance.y_vals = self.cleaned_data["y_vals"]
        if commit:
            instance.save()
        return instance
