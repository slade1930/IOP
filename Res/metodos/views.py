from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Simplex
from .forms import SimplexForm
from .serializers import SimplexSerializer
from .formula import simplex  # Asegúrate de tener esta función implementada


# =======================
# Vistas normales (Django)
# =======================
class SimplexListView(LoginRequiredMixin, ListView):
    model = Simplex
    template_name = "metodo/list_simplex.html"
    context_object_name = "resultados"

    def get_queryset(self):
        return Simplex.objects.filter(usuario=self.request.user)


class SimplexFormView(LoginRequiredMixin, CreateView):
    model = Simplex
    form_class = SimplexForm
    template_name = "metodo/add_simplex.html"
    success_url = reverse_lazy("list_simplex")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.usuario = self.request.user
        instance.save()  # Guardamos primero para tener ID

        try:
            resultado = simplex(instance)
            instance.resultado = resultado
            instance.save()
            messages.success(self.request, "Cálculo completado exitosamente!")
        except Exception as e:
            messages.error(self.request, f"Error en el cálculo: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)


# =======================
# Vistas API (DRF)
# =======================
class SimplexListCreateView(ListCreateAPIView):
    queryset = Simplex.objects.all()
    serializer_class = SimplexSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class SimplexDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Simplex.objects.all()
    serializer_class = SimplexSerializer
    permission_classes = [IsAuthenticated]
