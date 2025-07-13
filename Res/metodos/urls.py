from django.urls import path
from django.views.generic import TemplateView
from .views import (
    MetodoChatbotView,
    SimplexListView,
    SimplexCreateView,
    SimplexDetailView,
    SimplexListCreateView,
    SimplexDeleteView,
    SimplexDetailView as SimplexAPIDetailView,  # Alias para evitar conflicto de nombres
    # Falsa Posición
    FalsaPosicionListView,
    FalsaPosicionChatbotView,
    FalsaPosicionFormView,
    FalsaPosicionDeleteView,
    FalsaPosicionListCreateView,
    FalsaPosicionDetailView,
    # Eliminación Gaussiana
    GaussEliminacionListView,
    GaussEliminacionChatbotView,
    GaussEliminacionDeleteView,
    GaussEliminacionFormView,
    GaussEliminacionListCreateView,
    GaussEliminacionDetailView,
    # Gauss-Jordan
    GaussJordanChatbotView,
    GaussJordanListView,
    GaussJordanFormView,
    GaussJordanDeleteView,
    GaussJordanListCreateView,
    GaussJordanDetailView,
    # Diferenciación Finita
    DiferenciacionFinitaListView,
    DiferenciacionFinitaChatbotView,
    DiferenciacionFinitaCreateView,
    DiferenciacionFinitaDeleteView,
    DiferenciacionFinitaListCreateView,
    DiferenciacionFinitaDetailView,
    # Interpolación de Newton
    InterpolacionNewtonChatbotView,
    InterpolacionNewtonListView,
    InterpolacionNewtonCreateView,
    InterpolacionNewtonDeleteView,
    InterpolacionNewtonListCreateView,
    InterpolacionNewtonDetailView,
)

urlpatterns = [
    path("chatbot/metodo/", MetodoChatbotView.as_view(), name="chatbot_metodo"),
    # Vista de inicio
    path("", TemplateView.as_view(template_name="metodo/inicio.html"), name="inicio"),
    # Vistas normales (HTML)
    path("simplex/", SimplexListView.as_view(), name="list_simplex"),
    path("simplex/nuevo/", SimplexCreateView.as_view(), name="add_simplex"),
    # Vista detallada (HTML) - Asegúrate de que esta ruta esté antes que las API para prioridad
    path(
        "simplex/<int:pk>/",
        SimplexDetailView.as_view(template_name="metodo/detail_simplex.html"),
        name="detail_simplex",
    ),
    path(
        "simplex/delete/<int:pk>/", SimplexDeleteView.as_view(), name="delete_simplex"
    ),
    # Vistas API (JSON)
    path("api/simplex/", SimplexListCreateView.as_view(), name="api_simplex_list"),
    path(
        "api/simplex/<int:pk>/",
        SimplexAPIDetailView.as_view(),
        name="api_simplex_detail",
    ),
    # vistas API - FALSA POSICION
    path(
        "falsa-posicion/", FalsaPosicionListView.as_view(), name="list_falsa_posicion"
    ),
    path(
        "falsa-posicion/nuevo/",
        FalsaPosicionFormView.as_view(),
        name="add_falsa_posicion",
    ),
    path(
        "falsa-posicion/eliminar/<int:pk>/",  # Cambiado de id a pk
        FalsaPosicionDeleteView.as_view(),  # Usando la nueva vista basada en DeleteView
        name="delete_falsa_posicion",
    ),
    path(
        "falsa-posicion/chatbot/",
        FalsaPosicionChatbotView.as_view(),
        name="falsa_posicion_chatbot",
    ),
    # API Falsa Posición
    path(
        "api/falsa-posicion/",
        FalsaPosicionListCreateView.as_view(),
        name="api_falsa_posicion_list",
    ),
    path(
        "api/falsa-posicion/<int:pk>/",
        FalsaPosicionDetailView.as_view(),
        name="api_falsa_posicion_detail",
    ),
    # ------------------------- Eliminación Gaussiana -------------------------
    path("gauss/", GaussEliminacionListView.as_view(), name="list_gauss_eliminacion"),
    path(
        "gauss/nuevo/",
        GaussEliminacionFormView.as_view(),
        name="add_gauss_eliminacion",
    ),
    path(
        "gauss/eliminar/<int:pk>/",  # Cambiado de id a pk
        GaussEliminacionDeleteView.as_view(),  # Usando la nueva vista basada en DeleteView
        name="delete_gauss_eliminacion",
    ),
    path(
        "gauss-eliminacion/chatbot/",
        GaussEliminacionChatbotView.as_view(),
        name="gauss_eliminacion_chatbot",
    ),
    # API Eliminación Gaussiana
    path(
        "api/gauss/",
        GaussEliminacionListCreateView.as_view(),
        name="api_gauss_list",
    ),
    path(
        "api/gauss/<int:pk>/",
        GaussEliminacionDetailView.as_view(),
        name="api_gauss_detail",
    ),
    # ------------------------- Gauss-Jordan -------------------------
    path(
        "gauss-jordan/",
        GaussJordanListView.as_view(),
        name="list_gauss_jordan",
    ),
    path(
        "gauss-jordan/nuevo/",
        GaussJordanFormView.as_view(),
        name="add_gauss_jordan",
    ),
    path(
        "gauss-jordan/eliminar/<int:pk>/",  # Cambiado de id a pk
        GaussJordanDeleteView.as_view(),  # Nueva vista basada en DeleteView
        name="delete_gauss_jordan",
    ),
    path(
        "chatbot/gauss-jordan/",
        GaussJordanChatbotView.as_view(),
        name="chatbot_gauss_jordan",
    ),
    # API Gauss-Jordan
    path(
        "api/gauss-jordan/",
        GaussJordanListCreateView.as_view(),
        name="api_gauss_jordan_list",
    ),
    path(
        "api/gauss-jordan/<int:pk>/",
        GaussJordanDetailView.as_view(),
        name="api_gauss_jordan_detail",
    ),
    # ------------------------- Diferenciación Finita -------------------------
    path(
        "diferenciacion/",
        DiferenciacionFinitaListView.as_view(),
        name="list_diferenciacion_finita",
    ),
    path(
        "diferenciacion/nuevo/",
        DiferenciacionFinitaCreateView.as_view(),
        name="add_diferenciacion_finita",
    ),
    path(
        "diferenciacion/eliminar/<int:pk>/",  # Cambiado de id a pk
        DiferenciacionFinitaDeleteView.as_view(),  # Nueva vista basada en DeleteView
        name="delete_diferenciacion_finita",
    ),
    path(
        "chatbot/diferenciacion-finita/",
        DiferenciacionFinitaChatbotView.as_view(),
        name="chatbot_diferenciacion_finita",
    ),
    # API Diferenciación Finita
    path(
        "api/diferenciacion/",
        DiferenciacionFinitaListCreateView.as_view(),
        name="api_diferenciacion_list",
    ),
    path(
        "api/diferenciacion/<int:pk>/",
        DiferenciacionFinitaDetailView.as_view(),
        name="api_diferenciacion_detail",
    ),
    # ------------------------- Interpolación de Newton -------------------------
    path(
        "interpolacion/",
        InterpolacionNewtonListView.as_view(),
        name="list_interpolacion_newton",
    ),
    path(
        "interpolacion/nuevo/",
        InterpolacionNewtonCreateView.as_view(),
        name="add_interpolacion_newton",
    ),
    path(
        "interpolacion/eliminar/<int:pk>/",  # Cambiado de id a pk
        InterpolacionNewtonDeleteView.as_view(),  # Nueva vista basada en DeleteView
        name="delete_interpolacion_newton",
    ),
    path(
        "chatbot/interpolacion-newton/",
        InterpolacionNewtonChatbotView.as_view(),
        name="chatbot_interpolacion_newton",
    ),
    # API Interpolación de Newton
    path(
        "api/interpolacion/",
        InterpolacionNewtonListCreateView.as_view(),
        name="api_interpolacion_list",
    ),
    path(
        "api/interpolacion/<int:pk>/",
        InterpolacionNewtonDetailView.as_view(),
        name="api_interpolacion_detail",
    ),
]
