from django.urls import path
from django.views.generic import TemplateView

from .views import (
    SimplexListView,
    SimplexFormView,
    SimplexListCreateView,
    SimplexDetailView,
)

urlpatterns = [
    # Página de inicio (puedes mantenerla o ajustarla)
    path("", TemplateView.as_view(template_name="metodo/inicio.html"), name="inicio"),
    # Vistas normales
    path("simplex/", SimplexListView.as_view(), name="list_simplex"),
    path("simplex/nuevo/", SimplexFormView.as_view(), name="add_simplex"),
    # API endpoints
    path(
        "api/simplex/", SimplexListCreateView.as_view(), name="api_list_create_simplex"
    ),
    path(
        "api/simplex/<int:pk>/", SimplexDetailView.as_view(), name="api_detail_simplex"
    ),
]
