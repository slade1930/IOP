from math import *
import matplotlib.pyplot as plt
import numpy as np
import io
import base64


# ------------------ MÉTODO DE FALSA POSICIÓN ------------------
def falsa_posicion(funcion, x0, x1, tol=1e-4, max_iter=100):
    pasos = ""
    try:
        fx = lambda x: eval(funcion)

        for i in range(max_iter):
            f_x0 = fx(x0)
            f_x1 = fx(x1)

            if f_x0 == f_x1:
                pasos += "División por cero detectada. f(x0) = f(x1).\n"
                break

            x2 = x1 - (f_x1 * (x0 - x1)) / (f_x0 - f_x1)
            f_x2 = fx(x2)

            pasos += f"Iteración {i+1}: x0 = {x0:.6f}, x1 = {x1:.6f}, x2 = {x2:.6f}, f(x2) = {f_x2:.6f}\n"

            if abs(f_x2) < tol:
                pasos += f"Raíz aproximada encontrada: {x2:.6f}\n"
                return x2, pasos

            if f_x0 * f_x2 < 0:
                x1 = x2
            else:
                x0 = x2

        pasos += (
            f"No se encontró raíz con tolerancia {tol} en {max_iter} iteraciones.\n"
        )
        return x2, pasos

    except Exception as e:
        return None, f"Error al evaluar la función: {str(e)}"


def generar_grafica(funcion_str, x0, x1, raiz_aprox):
    try:
        fx = lambda x: eval(funcion_str)
        x_vals = np.linspace(x0 - 1, x1 + 1, 400)
        y_vals = [fx(x) for x in x_vals]

        plt.figure(figsize=(8, 5))
        plt.plot(x_vals, y_vals, label=f"f(x) = {funcion_str}")
        plt.axhline(0, color="gray", linestyle="--")
        plt.plot(
            raiz_aprox, fx(raiz_aprox), "ro", label=f"Raíz aprox: {raiz_aprox:.6f}"
        )
        plt.title("Método de Falsa Posición")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.legend()
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        imagen_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return imagen_base64
    except Exception as e:
        return None


# ------------------ MÉTODO DE ELIMINACIÓN DE GAUSS ------------------
def eliminacion_gauss(A, b):
    A = np.array(A, float)
    b = np.array(b, float)
    n = len(b)
    pasos = ""

    try:
        for i in range(n):
            if A[i][i] == 0:
                return None, "División por cero detectada en la diagonal."

            for j in range(i + 1, n):
                factor = A[j][i] / A[i][i]
                A[j, i:] -= factor * A[i, i:]
                b[j] -= factor * b[i]
                pasos += f"R{j+1} = R{j+1} - ({factor:.4f}) * R{i+1}\n"

        x = np.zeros(n)
        for i in range(n - 1, -1, -1):
            x[i] = (b[i] - np.dot(A[i, i + 1 :], x[i + 1 :])) / A[i][i]

        return x.tolist(), pasos
    except Exception as e:
        return None, f"Error durante la eliminación de Gauss: {str(e)}"


def grafica_comparacion_solucion(A, b, solucion):
    try:
        exacta = np.linalg.solve(np.array(A), np.array(b))
        indices = np.arange(len(b))

        plt.figure(figsize=(8, 5))
        plt.plot(indices, exacta, "go-", label="Solución exacta")
        plt.plot(indices, solucion, "ro--", label="Solución numérica (Gauss)")
        plt.title("Comparación: Solución Exacta vs Numérica")
        plt.xlabel("Variable")
        plt.ylabel("Valor")
        plt.legend()
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        imagen_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return imagen_base64
    except Exception as e:
        return None


# ------------------ MÉTODO DE GAUSS-JORDAN ------------------
def gauss_jordan(A, b, problema):
    A = np.array(A, float)
    b = np.array(b, float)
    n = len(b)
    pasos = []

    try:
        # Paso 1: Mostrar el problema planteado
        pasos.append(f"Problema económico planteado: {problema}")

        # Paso 2: Mostrar las ecuaciones
        ecuaciones = []
        for i in range(n):
            eq = " + ".join([f"{A[i,j]:.3f}x{j+1}" for j in range(n)])
            ecuaciones.append(f"{eq} = {b[i]:.2f}")
        pasos.append("\nSistema de ecuaciones:")
        pasos.extend(ecuaciones)

        # Proceso de Gauss-Jordan
        Ab = np.hstack([A, b.reshape(-1, 1)])
        pasos.append("\nIniciando eliminación de Gauss-Jordan:")

        for i in range(n):
            # Pivoteo parcial para evitar división por cero
            max_row = np.argmax(np.abs(Ab[i:, i])) + i
            if Ab[max_row, i] == 0:
                return (
                    None,
                    ["El sistema no tiene solución única (matriz singular)"],
                    None,
                )

            # Intercambiar filas si es necesario
            if max_row != i:
                Ab[[i, max_row]] = Ab[[max_row, i]]
                pasos.append(
                    f"\nIntercambiando fila {i+1} con fila {max_row+1} para mejor pivote"
                )

            # Normalizar la fila i
            divisor = Ab[i, i]
            Ab[i] = Ab[i] / divisor
            pasos.append(
                f"\nPaso {len(pasos)}: Normalizar fila {i+1} dividiendo por {divisor:.4f}"
            )
            pasos.append(f"R{i+1} = R{i+1} / {divisor:.4f}")
            pasos.append(f"Matriz actual:\n{np.round(Ab, 4)}")

            # Eliminación en otras filas
            for j in range(n):
                if i != j:
                    factor = Ab[j, i]
                    Ab[j] = Ab[j] - factor * Ab[i]
                    pasos.append(
                        f"\nPaso {len(pasos)}: Eliminar x{i+1} de la fila {j+1}"
                    )
                    pasos.append(f"R{j+1} = R{j+1} - ({factor:.4f}) * R{i+1}")
                    pasos.append(f"Matriz actual:\n{np.round(Ab, 4)}")

        x = Ab[:, -1]

        # Verificación de la solución
        if not np.allclose(np.dot(A, x), b, rtol=1e-3):
            return None, ["La solución no satisface el sistema original"], None

        # Interpretación económica de los resultados
        pasos.append("\nInterpretación económica:")
        for i in range(n):
            pasos.append(f"x{i+1} = ${x[i]:,.2f}")

        pasos.append("\nVerificación:")
        pasos.append(f"Inversión total: ${sum(x):,.2f}")
        if n == 3:  # Caso específico para problemas de inversión
            interes_calculado = 0.05 * x[0] + 0.08 * x[1] + 0.09 * x[2]
            pasos.append(
                f"Interés calculado: ${interes_calculado:,.2f} (debería ser $770.00)"
            )
            if abs(interes_calculado - 770) > 1.0:
                pasos.append(
                    "¡Advertencia: El interés calculado no coincide con el esperado!"
                )

        return x.tolist(), pasos, Ab[:, :-1]
    except Exception as e:
        return None, [f"Error durante Gauss-Jordan: {str(e)}"], None


def grafica_matriz_transformada(solucion, problema):
    try:
        plt.figure(figsize=(10, 6))

        # Definir colores y etiquetas según el tipo de inversión
        if len(solucion) == 3:
            categorias = ["5% interés", "8% interés", "9% interés"]
            colores = ["#4CAF50", "#2196F3", "#FF9800"]  # Verde, Azul, Naranja
        else:
            categorias = [f"Inversión {i+1}" for i in range(len(solucion))]
            colores = plt.cm.tab10.colors[: len(solucion)]

        # Crear gráfico de barras
        bars = plt.bar(categorias, solucion, color=colores)

        # Añadir valores y porcentajes
        total = sum(solucion)
        for bar in bars:
            height = bar.get_height()
            porcentaje = (height / total) * 100
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${height:,.2f}\n({porcentaje:.1f}%)",
                ha="center",
                va="bottom",
            )

        plt.title(
            f"Distribución de Inversiones\n{problema[:60]}..."
            if len(problema) > 60
            else f"Distribución de Inversiones\n{problema}"
        )
        plt.xlabel("Tipos de Inversión")
        plt.ylabel("Cantidad ($)")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()

        # Guardar gráfico
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        buf.seek(0)

        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        print(f"Error al generar gráfico: {e}")
        return None
