import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json
from matplotlib.patches import Polygon


def simplex(simplex_instance):
    """
    Implementación completa del método Simplex con generación de gráficos
    para problemas 2D.
    """
    # Extraer datos del modelo
    c = np.array(simplex_instance.coef_objetivo, dtype=float)
    A = np.array(simplex_instance.matriz_restricciones, dtype=float)
    b = np.array(simplex_instance.vector_b, dtype=float)
    desigualdades = simplex_instance.desigualdades
    problema = simplex_instance.tipo_problema

    # Validación para gráficos (solo funciona para 2 variables)
    if len(c) != 2:
        return ejecutar_simplex_sin_grafico(c, A, b, desigualdades, problema)

    # Ejecutar Simplex y generar gráfico
    resultado = ejecutar_simplex(c, A, b, desigualdades, problema)
    grafico_base64 = generar_grafico(c, A, b, desigualdades, problema, resultado)

    resultado["grafico"] = grafico_base64
    return resultado


def ejecutar_simplex(c, A, b, desigualdades, problema):
    """Algoritmo Simplex para problemas de programación lineal"""
    # Convertir a problema de maximización
    if problema == "min":
        c = -c

    # Número de variables y restricciones
    num_vars = len(c)
    num_restr = len(b)

    # Preparar la tabla simplex
    tabla = np.zeros((num_restr + 1, num_vars + num_restr + 1))

    # Llenar la tabla simplex
    for i in range(num_restr):
        tabla[i, :num_vars] = A[i]
        tabla[i, num_vars + i] = 1  # Variables de holgura
        tabla[i, -1] = b[i]

    # Función objetivo
    tabla[-1, :num_vars] = -c

    pasos = []
    pasos.append({"titulo": "Tabla inicial", "tabla": tabla.copy().tolist()})

    # Iteraciones Simplex
    iteracion = 0
    while True:
        iteracion += 1
        if iteracion > 100:
            raise ValueError("Número máximo de iteraciones alcanzado")

        # Verificar optimalidad
        if np.all(tabla[-1, :-1] >= 0):
            break

        # Seleccionar columna pivote (variable entrante)
        col_pivote = np.argmin(tabla[-1, :-1])

        # Seleccionar fila pivote (variable saliente)
        ratios = np.divide(
            tabla[:-1, -1],
            tabla[:-1, col_pivote],
            out=np.full(num_restr, np.inf),
            where=tabla[:-1, col_pivote] > 0,
        )
        fila_pivote = np.argmin(ratios)

        # Pivoteo
        pivote = tabla[fila_pivote, col_pivote]
        tabla[fila_pivote, :] /= pivote

        for i in range(num_restr + 1):
            if i != fila_pivote:
                tabla[i, :] -= tabla[i, col_pivote] * tabla[fila_pivote, :]

        pasos.append(
            {
                "titulo": f"Iteración {iteracion}",
                "tabla": tabla.copy().tolist(),
                "pivote": {"fila": fila_pivote, "columna": col_pivote},
            }
        )

    # Obtener solución
    solucion = np.zeros(num_vars)
    for i in range(num_vars):
        col = tabla[:, i]
        if np.sum(col == 1) == 1 and np.sum(col != 0) == 1:
            fila = np.where(col == 1)[0][0]
            solucion[i] = tabla[fila, -1]

    valor_optimo = tabla[-1, -1]
    if problema == "min":
        valor_optimo = -valor_optimo

    return {
        "solucion": solucion.tolist(),
        "valor_optimo": float(valor_optimo),
        "iteraciones": iteracion,
        "pasos": pasos,
        "grafico": None,
    }


def ejecutar_simplex_sin_grafico(c, A, b, desigualdades, problema):
    """Versión simplificada para problemas con más de 2 variables"""
    resultado = ejecutar_simplex(c, A, b, desigualdades, problema)
    resultado["grafico"] = None
    return resultado


def generar_grafico(c, A, b, desigualdades, problema, resultado):
    """Genera un gráfico de la región factible para problemas 2D"""
    plt.figure(figsize=(10, 8))

    # Configurar ejes
    x = np.linspace(0, max(b) * 1.5, 400)
    plt.xlim(0, max(b) * 1.2)
    plt.ylim(0, max(b) * 1.2)
    plt.xlabel("x₁")
    plt.ylabel("x₂")

    # Graficar restricciones
    vertices = []
    for i in range(len(A)):
        a1, a2 = A[i]
        bi = b[i]
        des = desigualdades[i]

        if a2 != 0:
            y = (bi - a1 * x) / a2
            label = f"{a1}x₁ + {a2}x₂ {des} {bi}"

            if des == "<=":
                plt.plot(x, y, label=label)
                plt.fill_between(x, 0, y, alpha=0.1)
            elif des == ">=":
                plt.plot(x, y, label=label)
                plt.fill_between(x, y, plt.ylim()[1], alpha=0.1)
        else:
            # Restricción vertical u horizontal
            pass

    # Graficar solución óptima
    if resultado["solucion"]:
        x_opt, y_opt = resultado["solucion"]
        plt.plot(
            x_opt,
            y_opt,
            "ro",
            markersize=10,
            label=f"Óptimo ({x_opt:.2f}, {y_opt:.2f})",
        )

    # Graficar función objetivo
    if len(c) == 2:
        z = resultado["valor_optimo"]
        y_obj = (z - c[0] * x) / c[1]
        plt.plot(x, y_obj, "k--", label=f"Z = {z:.2f}")

    plt.legend()
    plt.grid(True)
    plt.title("Región Factible y Solución Óptima")

    # Convertir gráfico a base64 para HTML
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return grafico_base64
