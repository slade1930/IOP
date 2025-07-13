import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import sympy as sp
from math import *

# ------------------ DIFERENCIACIÓN FINITA ------------------


def diferenciacion_finita(funcion, punto, h=0.01, orden=1, tipo="central"):
    """
    Calcula derivadas numéricas usando diferencias finitas con opciones avanzadas

    Args:
        funcion (str): Función matemática en términos de x
        x0 (float): Punto donde se evalúa la derivada
        h (float): Tamaño del paso (default: 0.01)
        orden (int): Orden de la derivada (1 o 2, default: 1)
        tipo (str): Tipo de diferencia ('adelante', 'atras', 'central', default: 'central')

    Returns:
        tuple: (valor_derivada, pasos, grafico_base64) o (None, error_msg, None) en caso de error
    """
    pasos = []
    try:
        # Convertir la función string a una función sympy
        x = sp.symbols("x")
        f = sp.sympify(funcion)

        # Validar parámetros
        if orden not in [1, 2]:
            raise ValueError("El orden debe ser 1 o 2")
        if tipo not in ["adelante", "atras", "central"]:
            raise ValueError("Tipo debe ser 'adelante', 'atras' o 'central'")
        if orden == 2 and tipo != "central":
            raise ValueError("Para orden 2 solo se soporta tipo 'central'")

        # Calcular la derivada según el tipo
        if orden == 1:
            if tipo == "adelante":
                derivada = (f.subs(x, punto + h) - f.subs(x, punto)) / h
                pasos.append("Fórmula de diferencia adelante (orden 1):")
                pasos.append(f"(f({punto + h}) - f({punto})) / {h} = {derivada:.6f}")
            elif tipo == "atras":
                derivada = (f.subs(x, punto) - f.subs(x, punto - h)) / h
                pasos.append("Fórmula de diferencia atrás (orden 1):")
                pasos.append(f"(f({punto}) - f({punto - h})) / {h} = {derivada:.6f}")
            else:  # central
                derivada = (f.subs(x, punto + h) - f.subs(x, punto - h)) / (2 * h)
                pasos.append("Fórmula de diferencia central (orden 1):")
                pasos.append(
                    f"(f({punto + h}) - f({punto - h})) / (2*{h}) = {derivada:.6f}"
                )
        else:  # orden == 2
            derivada = (
                f.subs(x, punto + h) - 2 * f.subs(x, punto) + f.subs(x, punto - h)
            ) / (h**2)
            pasos.append("Fórmula de diferencia central (orden 2):")
            pasos.append(
                f"(f({punto + h}) - 2f({punto}) + f({punto - h})) / {h}^2 = {derivada:.6f}"
            )

        # Generar gráfico
        grafica = grafica_diferenciacion(
            f, funcion, punto, h, float(derivada), orden, tipo
        )

        return float(derivada), "\n".join(pasos), grafica

    except Exception as e:
        return None, f"Error: {str(e)}", None


def grafica_diferenciacion(f_sympy, funcion_str, x0, h, derivada, orden, tipo):
    """
    Genera gráfico para diferenciación finita

    Args:
        f_sympy: Función sympy
        funcion_str (str): Representación string de la función
        x0 (float): Punto de evaluación
        h (float): Tamaño del paso
        derivada (float): Valor calculado de la derivada
        orden (int): Orden de derivada
        tipo (str): Tipo de diferencia

    Returns:
        str: Imagen en base64 o None en caso de error
    """
    try:
        x = sp.symbols("x")
        x_vals = np.linspace(x0 - 3 * h, x0 + 3 * h, 200)
        y_vals = [f_sympy.subs(x, val) for val in x_vals]

        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, label=f"f(x) = {funcion_str}")
        plt.scatter([x0], [f_sympy.subs(x, x0)], color="red", label=f"Punto x={x0}")

        if orden == 1:
            # Mostrar recta tangente
            pendiente = derivada
            intercepto = float(f_sympy.subs(x, x0)) - pendiente * x0
            tangente = pendiente * x_vals + intercepto
            plt.plot(
                x_vals,
                tangente,
                "--",
                label=f"Recta tangente (pendiente={pendiente:.4f})",
            )

        plt.title(
            f"Diferenciación {tipo} {'de orden '+str(orden) if orden>1 else ''} en x={x0}"
        )
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        buf.seek(0)

        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return None


# ------------------ INTERPOLACIÓN DE NEWTON ------------------


def interpolacion_newton(x_vals, y_vals, x_interp):
    pasos = []
    try:
        if len(x_vals) != len(y_vals):
            raise ValueError("Las listas x e y deben tener el mismo tamaño.")
        if len(x_vals) < 2:
            raise ValueError("Se necesitan al menos 2 puntos para interpolación.")
        if len(set(x_vals)) != len(x_vals):
            raise ValueError("Los valores de x deben ser distintos.")

        n = len(x_vals)
        x = sp.symbols("x")
        F = [[0] * n for _ in range(n)]
        for i in range(n):
            F[i][0] = y_vals[i]

        pasos.append("Tabla de diferencias divididas:")
        header = ["x_i", "f[x_i]"] + [f"Orden {j}" for j in range(1, n)]
        pasos.append("\t".join(header))

        for j in range(1, n):
            for i in range(n - j):
                F[i][j] = (F[i + 1][j - 1] - F[i][j - 1]) / (x_vals[i + j] - x_vals[i])

        for i in range(n):
            row = [f"{x_vals[i]:.4f}", f"{F[i][0]:.8f}"]
            for j in range(1, n):
                if j <= n - i - 1:
                    row.append(f"{F[i][j]:.8f}")
                else:
                    row.append("")
            pasos.append("\t".join(row))

        polinomio = F[0][0]
        producto = 1
        polinomio_str = f"{F[0][0]:.4f}"

        pasos.append("\nConstrucción del polinomio:")
        pasos.append(f"P(x) = {polinomio_str}")

        for j in range(1, n):
            producto *= x - x_vals[j - 1]
            termino = F[0][j] * producto
            polinomio += termino

            signo = "+" if F[0][j] >= 0 else "-"
            polinomio_str += f" {signo} {abs(F[0][j]):.4f}"
            for k in range(j):
                polinomio_str += f"(x-{x_vals[k]:.4f})"

            pasos.append(
                f"+ término {j}: {F[0][j]:.4f} * "
                + "".join([f"(x-{x_vals[k]:.4f})" for k in range(j)])
            )
            pasos.append(f"P(x) actual: {polinomio_str}")

        valor_interpolado = polinomio.subs(x, x_interp)
        pasos.append(f"\nEvaluación en x={x_interp}: {float(valor_interpolado):.6f}")

        grafica = grafica_interpolacion_newton(
            x_vals, y_vals, polinomio, x_interp, valor_interpolado
        )

        return (
            float(valor_interpolado),
            str(polinomio.expand()),
            "\n".join(pasos),
            grafica,
        )

    except Exception as e:
        return None, f"Error: {str(e)}", None, None  # Ahora devuelve siempre 4 valores.


def grafica_interpolacion_newton(x_vals, y_vals, polinomio, x_interp, y_interp):
    """
    Genera gráfico para interpolación de Newton

    Args:
        x_vals (list): Valores x conocidos
        y_vals (list): Valores y conocidos
        polinomio: Polinomio de interpolación (sympy)
        x_interp (float): Punto interpolado
        y_interp (float): Valor interpolado

    Returns:
        str: Imagen en base64 o None en caso de error
    """
    try:
        x = sp.symbols("x")
        x_min, x_max = min(x_vals), max(x_vals)
        x_range = x_max - x_min
        x_plot = np.linspace(x_min - 0.2 * x_range, x_max + 0.2 * x_range, 300)
        y_plot = [polinomio.subs(x, val) for val in x_plot]

        plt.figure(figsize=(10, 6))
        plt.plot(x_plot, y_plot, label="Polinomio interpolante")
        plt.scatter(x_vals, y_vals, color="red", label="Puntos conocidos", zorder=5)
        plt.scatter(
            [x_interp],
            [y_interp],
            color="green",
            label=f"Punto interpolado (x={x_interp:.2f}, y={y_interp:.2f})",
            zorder=5,
        )

        plt.axvline(x_interp, color="green", linestyle=":", alpha=0.5)
        plt.title("Interpolación de Newton")
        plt.xlabel("x")
        plt.ylabel("P(x)")
        plt.legend()
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        buf.seek(0)

        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception:
        return None
