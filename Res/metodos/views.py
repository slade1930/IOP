from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, View, DeleteView
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
import json
import warnings
import logging
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import logging
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .utils import (
    falsa_posicion,
    generar_grafica,
    eliminacion_gauss,
    gauss_jordan,
    grafica_comparacion_solucion,
    grafica_matriz_transformada,
)
from .forrmula import diferenciacion_finita, interpolacion_newton

from .models import (
    ProblemaSimplex,
    FalsaPosicion,
    GaussEliminacion,
    GaussJordan,
    DiferenciacionFinita,
    InterpolacionNewton,
)

from .forms import (
    FalsaPosicionForm,
    GaussEliminacionForm,
    GaussJordanForm,
    DiferenciacionFinitaForm,
    InterpolacionNewtonForm,
    SimplexForm,
)

from .serializers import (
    SimplexSerializer,
    FalsaPosicionSerializer,
    GaussEliminacionSerializer,
    GaussJordanSerializer,
    DiferenciacionFinitaSerializer,
    InterpolacionNewtonSerializer,
)
from .formula import resolver_simplex
from .chatgpt_utils import (
    generar_explicacion_simplex,
    FalsaPosicionChatbot,
    GaussEliminacionChatbot,
    GaussJordanChatbot,
    DiferenciasFinitasChatbot,
    InterpolacionChatbot,
    obtener_chatbot_metodo,
    responder_pregunta_metodo,
)

# Configuración de logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class MetodoChatbotView(View):
    def post(self, request, *args, **kwargs):
        print("Datos recibidos:", request.body)
        try:
            data = json.loads(request.body)
            print("Datos parseados:", data)
            metodo = data.get("metodo")
            pregunta = data.get("pregunta")
            contexto = data.get("contexto", {})

            if not metodo or not pregunta:
                return JsonResponse({"error": "Método o pregunta faltante"}, status=400)

            chatbot = obtener_chatbot_metodo(metodo)
            if not chatbot:
                return JsonResponse(
                    {"error": f"Método '{metodo}' no soportado"}, status=400
                )

            respuesta = chatbot.generar_respuesta(pregunta, contexto)
            return JsonResponse({"respuesta": respuesta})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


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
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                resultado = resolver_simplex(self.object)

                for warning in w:
                    messages.warning(self.request, str(warning.message))

            if resultado.get("error"):
                raise ValueError(resultado["error"])

            if not resultado.get("solucion"):
                raise ValueError("El solver no devolvió una solución válida")

            # Procesamiento de pasos
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

            # Generación de explicación con ChatGPT (versión mejorada)
            explicacion_ia = generar_explicacion_simplex(pasos_serializables)
            if not explicacion_ia:
                logger.warning(
                    "No se pudo generar explicación para el problema ID: %s",
                    self.object.id,
                )
                explicacion_ia = "No se pudo generar la explicación automática."

            # Guardar resultados
            self.object.pasos = pasos_serializables
            self.object.tabla_inicial = json.dumps(pasos[0]["tabla"]) if pasos else None
            self.object.tabla_final = json.dumps(resultado["tabla_final"])

            solucion_data = {
                "variables": resultado["solucion"],
                "valor_optimo": resultado["valor_optimo"],
                "optimalidad": resultado.get("optimalidad", "óptimo"),
                "iteraciones": resultado["iteraciones"],
                "variables_basicas_finales": resultado.get("variables_basicas", []),
            }
            self.object.solucion = json.dumps(solucion_data)
            self.object.grafico_base64 = resultado.get("grafico")
            self.object.variables_holgura = (
                len(resultado["solucion"]) - self.object.variables_decision
            )
            self.object.iteraciones_realizadas = resultado["iteraciones"]

            # Manejo de estados
            if resultado.get("optimalidad") == "no acotado":
                self.object.estado = "no_acotado"
            elif resultado.get("warning"):
                self.object.estado = "advertencia"
                self.object.advertencias = [resultado["warning"]]
            else:
                self.object.estado = "optimo"

            self.object.explicacion_chatgpt = explicacion_ia
            self.object.save()

            messages.success(self.request, "Problema resuelto exitosamente!")
            if resultado.get("warning"):
                messages.warning(self.request, resultado["warning"])

        except ValueError as e:
            logger.error("Error al resolver problema Simplex: %s", str(e))
            self.object.estado = "error"
            self.object.save()
            messages.error(self.request, f"Error al resolver el problema: {str(e)}")
            return self.form_invalid(form)
        except Exception as e:
            logger.exception("Error inesperado al procesar problema Simplex")
            self.object.estado = "error"
            self.object.save()
            messages.error(
                self.request,
                "Ocurrió un error inesperado. Por favor intenta nuevamente.",
            )
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

        # Procesamiento de solución
        solucion = None
        if problema.solucion:
            try:
                solucion = json.loads(problema.solucion)
            except json.JSONDecodeError as e:
                logger.error(
                    "Error decodificando solución JSON para problema ID %s: %s",
                    problema.id,
                    str(e),
                )
                solucion = None

        # Procesamiento de pasos
        pasos = problema.pasos if problema.pasos else []

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
        context["explicacion_chatgpt"] = problema.explicacion_chatgpt
        return context


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

            # Procesamiento de pasos
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

            # Generación de explicación con ChatGPT (versión mejorada)
            explicacion_ia = generar_explicacion_simplex(pasos_serializables)
            if not explicacion_ia:
                logger.warning(
                    "No se pudo generar explicación (API) para problema ID: %s",
                    problema.id,
                )
                explicacion_ia = "No se pudo generar la explicación automática."

            problema.pasos = pasos_serializables
            problema.tabla_inicial = json.dumps(pasos[0]["tabla"]) if pasos else None
            problema.tabla_final = json.dumps(resultado["tabla_final"])

            solucion_data = {
                "variables": resultado["solucion"],
                "valor_optimo": resultado["valor_optimo"],
                "optimalidad": resultado.get("optimalidad", "óptimo"),
                "iteraciones": resultado["iteraciones"],
                "variables_basicas_finales": resultado.get("variables_basicas", []),
            }
            problema.solucion = json.dumps(solucion_data)
            problema.grafico_base64 = resultado.get("grafico")
            problema.variables_holgura = (
                len(resultado["solucion"]) - problema.variables_decision
            )
            problema.iteraciones_realizadas = resultado["iteraciones"]

            # Manejo de estados
            if resultado.get("optimalidad") == "no acotado":
                problema.estado = "no_acotado"
            elif resultado.get("warning"):
                problema.estado = "advertencia"
                problema.advertencias = (problema.advertencias or []) + [
                    resultado["warning"]
                ]
            else:
                problema.estado = "optimo"

            problema.explicacion_chatgpt = explicacion_ia
            problema.save()

        except ValueError as e:
            logger.error("Error en API al resolver problema Simplex: %s", str(e))
            problema.estado = "error"
            problema.save()
            raise
        except Exception as e:
            logger.exception("Error inesperado en API al procesar problema Simplex")
            problema.estado = "error"
            problema.save()
            raise


class SimplexDeleteView(LoginRequiredMixin, DeleteView):
    model = ProblemaSimplex
    success_url = reverse_lazy("list_simplex")

    def get_queryset(self):
        return ProblemaSimplex.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Problema eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


class SimplexDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = SimplexSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProblemaSimplex.objects.filter(usuario=self.request.user)


class FalsaPosicionListView(LoginRequiredMixin, ListView):
    model = FalsaPosicion
    template_name = "metodo/list.html"
    context_object_name = "resultados"

    def get_queryset(self):
        return FalsaPosicion.objects.filter(usuario=self.request.user).order_by(
            "-creado"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información adicional si es necesaria para el chatbot
        return context


class FalsaPosicionFormView(LoginRequiredMixin, CreateView):
    model = FalsaPosicion
    form_class = FalsaPosicionForm
    template_name = "metodo/add.html"
    success_url = reverse_lazy("list_falsa_posicion")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.usuario = self.request.user

        try:
            resultado, pasos = falsa_posicion(
                funcion=instance.funcion,
                x0=instance.x0,
                x1=instance.x1,
                tol=instance.tolerancia,
                max_iter=instance.max_iteraciones,
            )

            # Guardamos los pasos del cálculo como JSON
            instance.resultado = json.dumps(pasos, indent=2)

            # Generar gráfica si se obtuvo un resultado válido
            if resultado is not None:
                grafico = generar_grafica(
                    instance.funcion, instance.x0, instance.x1, resultado
                )
                instance.grafico_base64 = grafico

            instance.save()
            messages.success(self.request, "Cálculo realizado exitosamente.")
        except Exception as e:
            messages.error(self.request, f"Error en el cálculo: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)


class FalsaPosicionDeleteView(LoginRequiredMixin, DeleteView):
    model = FalsaPosicion
    success_url = reverse_lazy("list_falsa_posicion")

    def get_queryset(self):
        return FalsaPosicion.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cálculo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


class FalsaPosicionDetailView(LoginRequiredMixin, DetailView):
    model = FalsaPosicion
    template_name = "metodo/detail_falsa_posicion.html"
    context_object_name = "resultado"

    def get_queryset(self):
        return FalsaPosicion.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pasos = []

        if self.object.resultado:
            try:
                pasos = json.loads(self.object.resultado)
            except (TypeError, json.JSONDecodeError):
                pasos = [{"error": "No se pudieron cargar los pasos"}]

        context["pasos"] = pasos
        context["explicacion_chatgpt"] = (
            self.object.explicacion_chatgpt or "No se generó explicación."
        )

        # Agregamos el contexto necesario para el chatbot
        context["chatbot_context"] = {
            "funcion": self.object.funcion,
            "x0": self.object.x0,
            "x1": self.object.x1,
            "tolerancia": self.object.tolerancia,
            "resultado": self.object.resultado,
            "pasos": pasos,
        }

        return context


@method_decorator(csrf_exempt, name="dispatch")
class FalsaPosicionChatbotView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pregunta = data.get("pregunta", "").strip()
            metodo_id = data.get("metodo_id", "").strip()

            if not pregunta:
                return JsonResponse(
                    {"error": "La pregunta no puede estar vacía"}, status=400
                )

            # Contexto base
            contexto = {"metodo": "falsa_posicion", "pregunta_general": True}

            # Si hay metodo_id, agregamos información específica
            if metodo_id:
                try:
                    metodo = FalsaPosicion.objects.get(
                        id=metodo_id, usuario=request.user
                    )
                    contexto.update(
                        {
                            "pregunta_general": False,
                            "funcion": metodo.funcion,
                            "intervalo": [metodo.x0, metodo.x1],
                            "tolerancia": metodo.tolerancia,
                            "iteraciones": metodo.max_iteraciones,
                            "resultado": metodo.resultado,
                        }
                    )
                except FalsaPosicion.DoesNotExist:
                    pass  # Continuamos con contexto general

            chatbot = FalsaPosicionChatbot()
            respuesta = chatbot.generar_respuesta(pregunta, contexto)

            return JsonResponse({"respuesta": respuesta, "contexto": contexto})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class GaussEliminacionListView(LoginRequiredMixin, ListView):
    model = GaussEliminacion
    template_name = "metodo/list_gauss.html"
    context_object_name = "resultados"
    paginate_by = 10

    def get_queryset(self):
        return GaussEliminacion.objects.filter(usuario=self.request.user).order_by(
            "-creado"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resultados_procesados = []
        for item in context["resultados"]:
            resultado_procesado = {
                "id": item.id,
                "matriz_a": item.matriz_a,
                "vector_b": item.vector_b,
                "creado": item.creado,
                "grafico_base64": item.grafico_base64,
                "matriz_a_parsed": json.loads(item.matriz_a) if item.matriz_a else None,
                "vector_b_parsed": json.loads(item.vector_b) if item.vector_b else None,
                "resultado_parsed": (
                    json.loads(item.resultado) if item.resultado else None
                ),
                "has_result": bool(item.resultado),
            }
            resultados_procesados.append(resultado_procesado)

        context["resultados_procesados"] = resultados_procesados
        return context


class GaussEliminacionFormView(LoginRequiredMixin, CreateView):
    model = GaussEliminacion
    form_class = GaussEliminacionForm
    template_name = "metodo/add_gauss.html"
    success_url = reverse_lazy("list_gauss_eliminacion")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.usuario = self.request.user

        try:
            matriz_a = json.loads(instance.matriz_a)
            vector_b = json.loads(instance.vector_b)

            solucion, pasos = eliminacion_gauss(matriz_a, vector_b)

            if solucion is not None:
                instance.resultado = json.dumps(
                    {
                        "solucion": solucion,
                        "pasos": pasos,
                        "matriz_a": matriz_a,
                        "vector_b": vector_b,
                    }
                )

                # Generar explicación con ChatGPT
                try:
                    contexto = {
                        "matriz": matriz_a,
                        "vector": vector_b,
                        "solucion": solucion,
                        "pasos": pasos,
                    }
                    chatbot = GaussEliminacionChatbot()
                    instance.explicacion_chatgpt = chatbot.generar_explicacion(contexto)
                except Exception as e:
                    instance.explicacion_chatgpt = (
                        f"No se pudo generar explicación: {str(e)}"
                    )

                grafico = grafica_comparacion_solucion(matriz_a, vector_b, solucion)
                if grafico:
                    instance.grafico_base64 = grafico

                instance.save()
                messages.success(self.request, "Cálculo realizado exitosamente!")
                return super().form_valid(form)
            else:
                messages.error(self.request, "Error en el cálculo: " + pasos)
                return self.form_invalid(form)

        except json.JSONDecodeError:
            messages.error(self.request, "Formato incorrecto en matriz o vector")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)


class GaussEliminacionDeleteView(LoginRequiredMixin, DeleteView):
    model = GaussEliminacion
    success_url = reverse_lazy("list_gauss_eliminacion")

    def get_queryset(self):
        return GaussEliminacion.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cálculo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


class GaussEliminacionDetailView(LoginRequiredMixin, DetailView):
    model = GaussEliminacion
    template_name = "metodo/detail_gauss.html"
    context_object_name = "resultado"

    def get_queryset(self):
        return GaussEliminacion.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resultado_data = (
            json.loads(self.object.resultado) if self.object.resultado else {}
        )

        context.update(
            {
                "solucion": resultado_data.get("solucion"),
                "pasos": resultado_data.get("pasos", []),
                "matriz_inicial": resultado_data.get("matriz_a"),
                "vector_inicial": resultado_data.get("vector_b"),
                "explicacion_chatgpt": self.object.explicacion_chatgpt
                or "No se generó explicación.",
                "chatbot_context": {
                    "matriz": resultado_data.get("matriz_a"),
                    "vector": resultado_data.get("vector_b"),
                    "solucion": resultado_data.get("solucion"),
                    "pasos": resultado_data.get("pasos", []),
                },
            }
        )
        return context


@method_decorator(csrf_exempt, name="dispatch")
class GaussEliminacionChatbotView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pregunta = data.get("pregunta", "").strip()
            metodo_id = data.get("metodo_id", "").strip()

            if not pregunta:
                return JsonResponse(
                    {"error": "La pregunta no puede estar vacía"}, status=400
                )

            # Contexto base
            contexto = {"metodo": "gauss_eliminacion", "pregunta_general": True}

            # Si hay metodo_id, agregamos información específica
            if metodo_id:
                try:
                    metodo = GaussEliminacion.objects.get(
                        id=metodo_id, usuario=request.user
                    )
                    resultado_data = (
                        json.loads(metodo.resultado) if metodo.resultado else {}
                    )

                    contexto.update(
                        {
                            "pregunta_general": False,
                            "matriz": resultado_data.get("matriz_a"),
                            "vector": resultado_data.get("vector_b"),
                            "solucion": resultado_data.get("solucion"),
                            "pasos": resultado_data.get("pasos", []),
                        }
                    )
                except GaussEliminacion.DoesNotExist:
                    pass  # Continuamos con contexto general

            chatbot = GaussEliminacionChatbot()
            respuesta = chatbot.generar_respuesta(pregunta, contexto)

            return JsonResponse({"respuesta": respuesta, "contexto": contexto})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# -------------------------------------- jordan --------------------------------------------


class GaussJordanListView(LoginRequiredMixin, ListView):
    model = GaussJordan
    template_name = "metodo/list_gauss_jordan.html"
    context_object_name = "resultados"
    paginate_by = 10

    def get_queryset(self):
        return GaussJordan.objects.filter(usuario=self.request.user).order_by("-creado")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["resultados_procesados"] = [
            {
                "id": item.id,
                "matriz_a": item.matriz_a,
                "vector_b": item.vector_b,
                "problema": item.problema,
                "creado": item.creado,
                "grafico_base64": item.grafico_base64,
                "matriz_a_parsed": json.loads(item.matriz_a) if item.matriz_a else None,
                "vector_b_parsed": json.loads(item.vector_b) if item.vector_b else None,
                "resultado_parsed": (
                    json.loads(item.resultado) if item.resultado else None
                ),
                "matriz_transformada_parsed": (
                    json.loads(item.matriz_transformada)
                    if item.matriz_transformada
                    else None
                ),
                "has_result": bool(item.resultado),
            }
            for item in context["resultados"]
        ]
        return context


class GaussJordanFormView(LoginRequiredMixin, CreateView):
    model = GaussJordan
    form_class = GaussJordanForm
    template_name = "metodo/add_gauss_jordan.html"
    success_url = reverse_lazy("list_gauss_jordan")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.usuario = self.request.user

        try:
            matriz_a = json.loads(instance.matriz_a)
            vector_b = json.loads(instance.vector_b)

            solucion, pasos, matriz_transformada = gauss_jordan(
                matriz_a, vector_b, instance.problema
            )

            if solucion is None:
                messages.error(self.request, f"Error en el cálculo: {pasos[0]}")
                return self.form_invalid(form)

            instance.resultado = json.dumps(
                {
                    "solucion": solucion,
                    "pasos": pasos,
                    "matriz_a": matriz_a,
                    "vector_b": vector_b,
                    "problema": instance.problema,
                }
            )

            if matriz_transformada is not None:
                instance.matriz_transformada = json.dumps(matriz_transformada.tolist())

            grafico = grafica_matriz_transformada(solucion, instance.problema)
            if grafico:
                instance.grafico_base64 = grafico

            # Generar explicación con ChatGPT
            try:
                contexto = {
                    "matriz": matriz_a,
                    "vector": vector_b,
                    "solucion": solucion,
                    "pasos": pasos,
                    "problema": instance.problema,
                }
                chatbot = GaussJordanChatbot()
                instance.explicacion_chatgpt = chatbot.generar_respuesta(
                    "Explica el procedimiento paso a paso", contexto
                )
            except Exception as e:
                instance.explicacion_chatgpt = (
                    f"No se pudo generar explicación: {str(e)}"
                )

            instance.save()
            messages.success(self.request, "Cálculo realizado exitosamente!")
            return super().form_valid(form)

        except json.JSONDecodeError:
            messages.error(self.request, "Formato incorrecto en la matriz o el vector.")
            return self.form_invalid(form)

        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return self.form_invalid(form)


class GaussJordanDeleteView(LoginRequiredMixin, DeleteView):
    model = GaussJordan
    success_url = reverse_lazy("list_gauss_jordan")

    def get_queryset(self):
        return GaussJordan.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cálculo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


class GaussJordanDetailView(LoginRequiredMixin, DetailView):
    model = GaussJordan
    template_name = "metodo/detail_gauss_jordan.html"
    context_object_name = "resultado"

    def get_queryset(self):
        return GaussJordan.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resultado_data = (
            json.loads(self.object.resultado) if self.object.resultado else {}
        )

        context.update(
            {
                "solucion": resultado_data.get("solucion"),
                "pasos": resultado_data.get("pasos", []),
                "matriz_inicial": resultado_data.get("matriz_a"),
                "vector_inicial": resultado_data.get("vector_b"),
                "explicacion_chatgpt": self.object.explicacion_chatgpt
                or "No se generó explicación.",
                "chatbot_context": {
                    "matriz": resultado_data.get("matriz_a"),
                    "vector": resultado_data.get("vector_b"),
                    "solucion": resultado_data.get("solucion"),
                    "pasos": resultado_data.get("pasos", []),
                    "problema": resultado_data.get("problema"),
                },
            }
        )
        return context


@method_decorator(csrf_exempt, name="dispatch")
class GaussJordanChatbotView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pregunta = data.get("pregunta", "").strip()
            metodo_id = data.get("metodo_id", "").strip()

            if not pregunta:
                return JsonResponse(
                    {"error": "La pregunta no puede estar vacía"}, status=400
                )

            contexto = {"metodo": "gauss_jordan", "pregunta_general": True}

            if metodo_id:
                try:
                    metodo = GaussJordan.objects.get(id=metodo_id, usuario=request.user)
                    resultado_data = (
                        json.loads(metodo.resultado) if metodo.resultado else {}
                    )

                    contexto.update(
                        {
                            "pregunta_general": False,
                            "matriz": resultado_data.get("matriz_a"),
                            "vector": resultado_data.get("vector_b"),
                            "solucion": resultado_data.get("solucion"),
                            "pasos": resultado_data.get("pasos", []),
                            "problema": resultado_data.get("problema"),
                        }
                    )
                except GaussJordan.DoesNotExist:
                    pass  # Se mantiene el contexto general

            chatbot = GaussJordanChatbot()
            respuesta = chatbot.generar_respuesta(pregunta, contexto)

            return JsonResponse({"respuesta": respuesta, "contexto": contexto})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------- diferenciacion -----------------------------------------


class DiferenciacionFinitaListView(LoginRequiredMixin, ListView):
    model = DiferenciacionFinita
    template_name = "metodo/list_finita.html"
    context_object_name = "resultados"
    paginate_by = 10

    def get_queryset(self):
        return DiferenciacionFinita.objects.filter(usuario=self.request.user).order_by(
            "-creado"
        )


class DiferenciacionFinitaCreateView(LoginRequiredMixin, CreateView):
    model = DiferenciacionFinita
    form_class = DiferenciacionFinitaForm
    template_name = "metodo/add_finita.html"
    success_url = reverse_lazy("list_diferenciacion_finita")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.usuario = self.request.user

        try:
            resultado, pasos, grafico = diferenciacion_finita(
                funcion=instance.funcion,
                punto=instance.punto,
                h=instance.h,
                orden=instance.orden,
                tipo=instance.tipo,
            )

            instance.resultado = {
                "valor": resultado,
                "tipo": instance.tipo,
                "orden": instance.orden,
                "funcion": instance.funcion,
                "punto": instance.punto,
                "h": instance.h,
            }

            # Preparar resumen para el chatbot (no pasos completos)
            resumen = [
                {
                    "metodo": instance.tipo,
                    "resultado": resultado,
                    "error": self._calcular_error_estimado(
                        resultado, instance.funcion, instance.punto
                    ),
                }
            ]

            try:
                contexto = {
                    "funcion": instance.funcion,
                    "x": instance.punto,
                    "h": instance.h,
                    "orden": instance.orden,
                    "metodos": [instance.tipo],
                    "pasos": resumen,  # Solo el resumen de resultados
                }
                chatbot = DiferenciasFinitasChatbot()
                instance.explicacion_chatgpt = chatbot.generar_respuesta(
                    "Explica el cálculo realizado con diferencias finitas", contexto
                )
            except Exception as e:
                instance.explicacion_chatgpt = (
                    f"No se pudo generar explicación: {str(e)}"
                )

            instance.grafico_base64 = grafico
            instance.save()

            messages.success(self.request, "Cálculo realizado exitosamente!")
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Error en el cálculo: {str(e)}")
            return self.form_invalid(form)

    def _calcular_error_estimado(self, resultado, funcion_str, x):
        try:
            from sympy import sympify, diff

            f = sympify(funcion_str)
            derivada_real = float(diff(f).subs("x", x))
            return abs(derivada_real - resultado)
        except Exception:
            return "N/A"


class DiferenciacionFinitaDeleteView(LoginRequiredMixin, DeleteView):
    model = DiferenciacionFinita
    success_url = reverse_lazy("list_diferenciacion_finita")

    def get_queryset(self):
        return DiferenciacionFinita.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cálculo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


class DiferenciacionFinitaDetailView(LoginRequiredMixin, DetailView):
    model = DiferenciacionFinita
    template_name = "metodo/detail_finita.html"
    context_object_name = "resultado"

    def get_queryset(self):
        return DiferenciacionFinita.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resultado_data = self.object.resultado or {}

        resumen = [
            {
                "metodo": resultado_data.get("tipo"),
                "resultado": resultado_data.get("valor"),
                "error": self._calcular_error_estimado(
                    resultado_data.get("valor"),
                    resultado_data.get("funcion"),
                    resultado_data.get("punto"),
                ),
            }
        ]

        context.update(
            {
                "valor": resultado_data.get("valor"),
                "tipo": resultado_data.get("tipo"),
                "orden": resultado_data.get("orden"),
                "funcion": resultado_data.get("funcion"),
                "punto": resultado_data.get("punto"),
                "h": resultado_data.get("h"),
                "explicacion_chatgpt": self.object.explicacion_chatgpt
                or "No se generó explicación.",
                "chatbot_context": {
                    "funcion": resultado_data.get("funcion"),
                    "x": resultado_data.get("punto"),
                    "h": resultado_data.get("h"),
                    "orden": resultado_data.get("orden"),
                    "metodos": [resultado_data.get("tipo")],
                    "pasos": resumen,
                },
            }
        )
        return context

    def _calcular_error_estimado(self, resultado, funcion_str, x):
        try:
            from sympy import sympify, diff

            f = sympify(funcion_str)
            derivada_real = float(diff(f).subs("x", x))
            return abs(derivada_real - resultado)
        except Exception:
            return "N/A"


@method_decorator(csrf_exempt, name="dispatch")
class DiferenciacionFinitaChatbotView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pregunta = data.get("pregunta", "").strip()
            metodo_id = data.get("metodo_id", "").strip()

            if not pregunta:
                return JsonResponse(
                    {"error": "La pregunta no puede estar vacía"}, status=400
                )

            contexto = {"metodo": "diferencias_finitas", "pregunta_general": True}

            if metodo_id:
                try:
                    metodo = DiferenciacionFinita.objects.get(
                        id=metodo_id, usuario=request.user
                    )
                    resultado_data = metodo.resultado or {}

                    resumen = [
                        {
                            "metodo": resultado_data.get("tipo"),
                            "resultado": resultado_data.get("valor"),
                            "error": self._calcular_error_estimado(
                                resultado_data.get("valor"),
                                resultado_data.get("funcion"),
                                resultado_data.get("punto"),
                            ),
                        }
                    ]

                    contexto.update(
                        {
                            "pregunta_general": False,
                            "funcion": resultado_data.get("funcion"),
                            "x": resultado_data.get("punto"),
                            "h": resultado_data.get("h"),
                            "orden": resultado_data.get("orden"),
                            "metodos": [resultado_data.get("tipo")],
                            "pasos": resumen,
                        }
                    )
                except DiferenciacionFinita.DoesNotExist:
                    pass

            chatbot = DiferenciasFinitasChatbot()
            respuesta = chatbot.generar_respuesta(pregunta, contexto)

            return JsonResponse({"respuesta": respuesta, "contexto": contexto})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def _calcular_error_estimado(self, resultado, funcion_str, x):
        try:
            from sympy import sympify, diff

            f = sympify(funcion_str)
            derivada_real = float(diff(f).subs("x", x))
            return abs(derivada_real - resultado)
        except Exception:
            return "N/A"


# ---------------------------------------------- interpolacion ----------------------------------


class InterpolacionNewtonListView(LoginRequiredMixin, ListView):
    model = InterpolacionNewton
    template_name = "metodo/list_inter.html"
    context_object_name = "resultados"
    paginate_by = 10

    def get_queryset(self):
        return InterpolacionNewton.objects.filter(usuario=self.request.user).order_by(
            "-creado"
        )


class InterpolacionNewtonCreateView(LoginRequiredMixin, CreateView):
    model = InterpolacionNewton
    form_class = InterpolacionNewtonForm
    template_name = "metodo/add_inter.html"
    success_url = reverse_lazy("list_interpolacion_newton")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.usuario = self.request.user

        try:
            if not isinstance(instance.x_vals, list) or not isinstance(
                instance.y_vals, list
            ):
                messages.error(self.request, "Los valores x e y deben ser listas.")
                return self.form_invalid(form)

            if not isinstance(instance.x_interpolar, (float, int)):
                messages.error(
                    self.request, "El valor a interpolar debe ser un número."
                )
                return self.form_invalid(form)

            resultado, polinomio, pasos, grafico = interpolacion_newton(
                x_vals=instance.x_vals,
                y_vals=instance.y_vals,
                x_interp=instance.x_interpolar,
            )

            if resultado is None:
                messages.error(self.request, f"Error en el cálculo: {polinomio}")
                return self.form_invalid(form)

            instance.resultado = {
                "valor": resultado,
                "pasos": pasos,
                "x_vals": instance.x_vals,
                "y_vals": instance.y_vals,
                "x_interpolar": instance.x_interpolar,
            }
            instance.polinomio = polinomio
            instance.grafico_base64 = grafico

            # Generar explicación con ChatGPT (OPTIMIZADO)
            try:
                coeficientes = [str(p.get("coeficiente", "N/A")) for p in pasos]

                contexto = {
                    "metodo": "Newton",
                    "puntos": [
                        {"x": x, "y": y}
                        for x, y in zip(instance.x_vals, instance.y_vals)
                    ],
                    "grado": len(instance.x_vals) - 1,
                    "polinomio": polinomio,
                    "coeficientes": coeficientes,
                }

                chatbot = InterpolacionChatbot()
                instance.explicacion_chatgpt = chatbot.generar_respuesta(
                    "Explica el proceso de interpolación con el método de Newton",
                    contexto,
                )
            except Exception as e:
                instance.explicacion_chatgpt = (
                    f"No se pudo generar explicación: {str(e)}"
                )

            instance.save()
            messages.success(self.request, "Interpolación realizada exitosamente.")
            return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Error en el cálculo: {str(e)}")
            return self.form_invalid(form)


class InterpolacionNewtonDeleteView(LoginRequiredMixin, DeleteView):
    model = InterpolacionNewton
    success_url = reverse_lazy("list_interpolacion_newton")

    def get_queryset(self):
        return InterpolacionNewton.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cálculo eliminado correctamente.")
        return super().delete(request, *args, **kwargs)


class InterpolacionNewtonDetailView(LoginRequiredMixin, DetailView):
    model = InterpolacionNewton
    template_name = "metodo/detail_inter.html"
    context_object_name = "resultado"

    def get_queryset(self):
        return InterpolacionNewton.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resultado_data = self.object.resultado or {}

        coeficientes = [
            str(p.get("coeficiente", "N/A")) for p in resultado_data.get("pasos", [])
        ]

        context.update(
            {
                "valor": resultado_data.get("valor"),
                "pasos": resultado_data.get("pasos", []),
                "x_vals": resultado_data.get("x_vals", []),
                "y_vals": resultado_data.get("y_vals", []),
                "x_interpolar": resultado_data.get("x_interpolar"),
                "polinomio": self.object.polinomio,
                "explicacion_chatgpt": self.object.explicacion_chatgpt
                or "No se generó explicación.",
                "chatbot_context": {
                    "metodo": "Newton",
                    "puntos": [
                        {"x": x, "y": y}
                        for x, y in zip(
                            resultado_data.get("x_vals", []),
                            resultado_data.get("y_vals", []),
                        )
                    ],
                    "grado": len(resultado_data.get("x_vals", [])) - 1,
                    "polinomio": self.object.polinomio,
                    "coeficientes": coeficientes,
                },
            }
        )
        return context


@method_decorator(csrf_exempt, name="dispatch")
class InterpolacionNewtonChatbotView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pregunta = data.get("pregunta", "").strip()
            metodo_id = data.get("metodo_id", "").strip()

            if not pregunta:
                return JsonResponse(
                    {"error": "La pregunta no puede estar vacía"}, status=400
                )

            contexto = {"metodo": "interpolacion_newton", "pregunta_general": True}

            if metodo_id:
                try:
                    metodo = InterpolacionNewton.objects.get(
                        id=metodo_id, usuario=request.user
                    )
                    resultado_data = metodo.resultado or {}

                    coeficientes = [
                        str(p.get("coeficiente", "N/A"))
                        for p in resultado_data.get("pasos", [])
                    ]

                    contexto.update(
                        {
                            "pregunta_general": False,
                            "metodo": "Newton",
                            "puntos": [
                                {"x": x, "y": y}
                                for x, y in zip(
                                    resultado_data.get("x_vals", []),
                                    resultado_data.get("y_vals", []),
                                )
                            ],
                            "grado": len(resultado_data.get("x_vals", [])) - 1,
                            "polinomio": metodo.polinomio,
                            "coeficientes": coeficientes,
                        }
                    )
                except InterpolacionNewton.DoesNotExist:
                    pass

            chatbot = InterpolacionChatbot()
            respuesta = chatbot.generar_respuesta(pregunta, contexto)

            return JsonResponse({"respuesta": respuesta, "contexto": contexto})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# ------------------- API Falsa Posición -------------------


class FalsaPosicionListCreateView(ListCreateAPIView):
    queryset = FalsaPosicion.objects.all()
    serializer_class = FalsaPosicionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class FalsaPosicionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FalsaPosicion.objects.all()
    serializer_class = FalsaPosicionSerializer
    permission_classes = [IsAuthenticated]


# ------------------- API Gauss Eliminación -------------------


class GaussEliminacionListCreateView(ListCreateAPIView):
    queryset = GaussEliminacion.objects.all()
    serializer_class = GaussEliminacionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class GaussEliminacionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = GaussEliminacion.objects.all()
    serializer_class = GaussEliminacionSerializer
    permission_classes = [IsAuthenticated]


# -------------------API Gauss Jordan -------------------


class GaussJordanListCreateView(ListCreateAPIView):
    queryset = GaussJordan.objects.all()
    serializer_class = GaussJordanSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class GaussJordanDetailView(RetrieveUpdateDestroyAPIView):
    queryset = GaussJordan.objects.all()
    serializer_class = GaussJordanSerializer
    permission_classes = [IsAuthenticated]


# ------------------- API Interpolación de Newton -------------------


class InterpolacionNewtonListCreateView(ListCreateAPIView):
    queryset = InterpolacionNewton.objects.all()
    serializer_class = InterpolacionNewtonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class InterpolacionNewtonDetailView(RetrieveUpdateDestroyAPIView):
    queryset = InterpolacionNewton.objects.all()
    serializer_class = InterpolacionNewtonSerializer
    permission_classes = [IsAuthenticated]


# ------------------- API Diferenciación Finita -------------------


class DiferenciacionFinitaListCreateView(ListCreateAPIView):
    queryset = DiferenciacionFinita.objects.all()
    serializer_class = DiferenciacionFinitaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class DiferenciacionFinitaDetailView(RetrieveUpdateDestroyAPIView):
    queryset = DiferenciacionFinita.objects.all()
    serializer_class = DiferenciacionFinitaSerializer
    permission_classes = [IsAuthenticated]
