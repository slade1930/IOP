from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
import json
import warnings

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import ProblemaSimplex
from .forms import SimplexForm
from .serializers import SimplexSerializer
from .formula import resolver_simplex


class SimplexListView(LoginRequiredMixin, ListView):
    model = ProblemaSimplex
    template_name = "metodo/list_simplex.html"
    context_object_name = "problemas"
    paginate_by = 10

    def get_queryset(self):
        return ProblemaSimplex.objects.filter(usuario=self.request.user).order_by(
            "-creado"
        )


class SimplexCreateView(LoginRequiredMixin, CreateView):
    model = ProblemaSimplex
    form_class = SimplexForm
    template_name = "metodo/add_simplex.html"
    success_url = reverse_lazy("list_simplex")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        self.object = form.save()

        try:
            # Resolver el problema con manejo de warnings
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                resultado = resolver_simplex(self.object)

                # Mostrar warnings como mensajes
                for warning in w:
                    messages.warning(self.request, str(warning.message))

            # Manejar errores explícitos
            if resultado.get("error"):
                raise ValueError(resultado["error"])

            # Validación de solución
            if not resultado.get("solucion"):
                raise ValueError("El solver no devolvió una solución válida")

            # Procesar y guardar todos los pasos del simplex
            pasos = resultado.get("pasos", [])

            # Convertir numpy arrays a listas si es necesario
            pasos_serializables = []
            for paso in pasos:
                paso_serializado = {
                    "titulo": paso.get("titulo", "Paso"),
                    "tabla": (
                        paso["tabla"].tolist()
                        if hasattr(paso["tabla"], "tolist")
                        else paso["tabla"]
                    ),
                    "explicacion": paso.get("explicacion", ""),
                    "variables_basicas": paso.get("variables_basicas", []),
                    "pivote": paso.get("pivote", {}),
                }
                pasos_serializables.append(paso_serializado)

            # Guardar resultados
            self.object.pasos = pasos_serializables
            self.object.tabla_inicial = json.dumps(pasos[0]["tabla"]) if pasos else None
            self.object.tabla_final = json.dumps(resultado["tabla_final"])

            # Estructura mejorada de la solución
            solucion_data = {
                "variables": resultado["solucion"],
                "valor_optimo": resultado["valor_optimo"],
                "optimalidad": resultado.get("optimalidad", "óptimo"),
                "iteraciones": resultado["iteraciones"],
                "variables_basicas_finales": resultado.get("variables_basicas", []),
            }
            self.object.solucion = json.dumps(solucion_data)

            # Manejo condicional del gráfico
            self.object.grafico_base64 = resultado.get("grafico")
            self.object.variables_holgura = (
                len(resultado["solucion"]) - self.object.variables_decision
            )
            self.object.iteraciones_realizadas = resultado["iteraciones"]

            # Determinar estado del problema
            if resultado.get("optimalidad") == "no acotado":
                self.object.estado = "no_acotado"
            elif resultado.get("warning"):
                self.object.estado = "advertencia"
                self.object.advertencias = [resultado["warning"]]
            else:
                self.object.estado = "optimo"

            self.object.save()

            messages.success(self.request, "Problema resuelto exitosamente!")
            if resultado.get("warning"):
                messages.warning(self.request, resultado["warning"])

        except Exception as e:
            self.object.estado = "error"
            self.object.save()
            messages.error(self.request, f"Error al resolver el problema: {str(e)}")
            return self.form_invalid(form)

        return redirect(self.get_success_url())


class SimplexDetailView(LoginRequiredMixin, DetailView):
    model = ProblemaSimplex
    template_name = "metodo/detail_simplex.html"
    context_object_name = "problema"

    def get_queryset(self):
        return ProblemaSimplex.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problema = self.object

        # Cargar datos de solución
        solucion = None
        if problema.solucion:
            try:
                solucion = json.loads(problema.solucion)
            except json.JSONDecodeError:
                solucion = None

        # Cargar pasos del simplex
        pasos = problema.pasos if problema.pasos else []

        # Si no hay pasos pero hay tablas inicial/final, crear pasos básicos
        if not pasos and problema.tabla_inicial and problema.tabla_final:
            pasos = [
                {
                    "titulo": "Tabla Inicial",
                    "tabla": json.loads(problema.tabla_inicial),
                    "explicacion": "Tabla inicial del método Simplex",
                },
                {
                    "titulo": "Tabla Final",
                    "tabla": json.loads(problema.tabla_final),
                    "explicacion": "Tabla final con la solución óptima",
                },
            ]

        # Preparar datos para el template
        datos_completos = {
            "solucion": solucion,
            "pasos": pasos,
            "grafica": problema.grafico_base64,
            "es_2d": problema.variables_decision == 2,
            "estado": problema.estado,
            "iteraciones": problema.iteraciones_realizadas,
            "tabla_inicial": (
                json.loads(problema.tabla_inicial) if problema.tabla_inicial else None
            ),
            "tabla_final": (
                json.loads(problema.tabla_final) if problema.tabla_final else None
            ),
        }

        context["datos_completos"] = datos_completos
        return context


# Vistas API (DRF)
class SimplexListCreateView(ListCreateAPIView):
    serializer_class = SimplexSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProblemaSimplex.objects.filter(usuario=self.request.user).order_by(
            "-creado"
        )

    def perform_create(self, serializer):
        problema = serializer.save(usuario=self.request.user)

        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                resultado = resolver_simplex(problema)

                if w:
                    problema.advertencias = [str(warn.message) for warn in w]

            if resultado.get("error"):
                problema.estado = "error"
                problema.save()
                raise ValueError(resultado["error"])

            if not resultado.get("solucion"):
                problema.estado = "error"
                problema.save()
                raise ValueError("No se encontró solución válida")

            # Procesar pasos para la API
            pasos = resultado.get("pasos", [])
            pasos_serializables = []
            for paso in pasos:
                paso_serializado = {
                    "titulo": paso.get("titulo", "Paso"),
                    "tabla": (
                        paso["tabla"].tolist()
                        if hasattr(paso["tabla"], "tolist")
                        else paso["tabla"]
                    ),
                    "explicacion": paso.get("explicacion", ""),
                    "variables_basicas": paso.get("variables_basicas", []),
                    "pivote": paso.get("pivote", {}),
                }
                pasos_serializables.append(paso_serializado)

            problema.pasos = pasos_serializables
            problema.tabla_inicial = json.dumps(pasos[0]["tabla"]) if pasos else None
            problema.tabla_final = json.dumps(resultado["tabla_final"])

            solucion_data = {
                "variables": resultado["solucion"],
                "valor_optimo": resultado["valor_optimo"],
                "iteraciones": resultado["iteraciones"],
                "optimalidad": resultado.get("optimalidad", "óptimo"),
                "variables_basicas_finales": resultado.get("variables_basicas", []),
            }
            problema.solucion = json.dumps(solucion_data)
            problema.grafico_base64 = resultado.get("grafico")
            problema.variables_holgura = (
                len(resultado["solucion"]) - problema.variables_decision
            )
            problema.iteraciones_realizadas = resultado["iteraciones"]

            if resultado.get("optimalidad") == "no acotado":
                problema.estado = "no_acotado"
            elif resultado.get("warning"):
                problema.estado = "advertencia"
                problema.advertencias = (
                    problema.advertencias + [resultado["warning"]]
                    if problema.advertencias
                    else [resultado["warning"]]
                )
            else:
                problema.estado = "optimo"

            problema.save()

        except Exception as e:
            problema.estado = "error"
            problema.save()
            raise


class SimplexDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = SimplexSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProblemaSimplex.objects.filter(usuario=self.request.user)
