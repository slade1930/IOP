from openai import OpenAI
from django.conf import settings
from django.utils.safestring import mark_safe
from typing import List, Dict, Optional, Union
import logging
import json

# Configuración de logging
logger = logging.getLogger(__name__)

# Cliente OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)


# ===============================
# ===== PROMPT SIMPLEX ==========
# ===============================
def construir_prompt_simplex(pasos: List[Dict]) -> str:
    if not pasos:
        raise ValueError("La lista de pasos no puede estar vacía")

    pasos_texto = "\n".join(
        f"**Paso {i + 1}**: {paso.get('explicacion', 'Descripción no disponible')}\n"
        f"- Tabla: {paso.get('tabla', 'N/A')}\n"
        f"- Variables básicas: {paso.get('variables_basicas', [])}"
        for i, paso in enumerate(pasos)
    )

    return f"""
Eres un profesor experto en Investigación de Operaciones. Explica el procedimiento del método Simplex 
para el siguiente problema, siguiendo estas instrucciones:

1. **Contexto**: Breve introducción al método (1-2 oraciones).
2. **Explicación por pasos**: Describe qué ocurre en cada paso y por qué es importante.
3. **Conclusión**: Resumen del resultado y su interpretación.

**Datos del problema:**
{pasos_texto}

**Requisitos:**
- Lenguaje claro y didáctico.
- Máximo 500 palabras.
- Destaca los conceptos clave (pivote, variables básicas, optimalidad).
- Usa Markdown para formato (títulos, listas, énfasis).
"""


def generar_explicacion_simplex(pasos: List[Dict]) -> Optional[str]:
    if not pasos:
        logger.warning("Se intentó generar una explicación sin pasos")
        return None

    try:
        prompt = construir_prompt_simplex(pasos)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente especializado en matemáticas aplicadas. "
                        "Respuestas claras, técnicas pero accesibles. Usa Markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=800,
            top_p=0.9,
            frequency_penalty=0.2,
        )

        explicacion = response.choices[0].message.content
        mensaje_personalizado = "\n\n> **Nota:** Este método es más difícil que quitarle lo negro a Luis Castillo"
        return mark_safe(f"{explicacion}{mensaje_personalizado}")

    except Exception as e:
        logger.error(f"Error al generar explicación: {str(e)}", exc_info=True)
        return f"⚠️ Error al generar explicación: {str(e)}"


# ==========================================
# ===== CHATBOT BASE (Clase Abstracta) =====
# ==========================================
class MetodoNumericoChatbot:
    """Clase base para todos los chatbots de métodos numéricos"""

    def __init__(self):
        self.model_name = "gpt-4"  # Modelo por defecto
        self.temperature = 0.7
        self.max_tokens = 1000
        self.system_message = "Eres un asistente experto en métodos numéricos."

    def construir_contexto_inicial(self, problema: Dict) -> str:
        """Construye el contexto inicial para el chatbot"""
        raise NotImplementedError

    def generar_respuesta(self, pregunta: str, contexto: Dict = None) -> str:
        """Genera una respuesta a la pregunta del usuario"""
        try:
            messages = [
                {"role": "system", "content": self.system_message},
                {
                    "role": "user",
                    "content": (
                        self.construir_contexto_inicial(contexto) if contexto else ""
                    ),
                },
                {"role": "user", "content": pregunta},
            ]

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error en generar_respuesta: {str(e)}", exc_info=True)
            return f"⚠️ Error al procesar tu pregunta: {str(e)}"

    def generar_explicacion_metodo(self, pasos: List[Dict]) -> str:
        """Genera una explicación del método (para mantener compatibilidad)"""
        raise NotImplementedError


class FalsaPosicionChatbot(MetodoNumericoChatbot):
    def __init__(self):
        super().__init__()
        self.system_message = """
Eres un experto en el método de Falsa Posición (Regula Falsi) para encontrar raíces de ecuaciones. 
Debes responder de dos formas según el contexto:

1. Para preguntas GENERALES (sin datos específicos):
- Explica conceptos teóricos
- Describe el algoritmo paso a paso
- Proporciona ejemplos ilustrativos
- Da consejos de implementación

2. Para preguntas ESPECÍFICAS (con datos de un cálculo):
- Analiza los resultados concretos
- Explica cada paso del cálculo
- Evalúa la convergencia
- Sugiere mejoras para el caso específico

Usa Markdown para formatear tus respuestas con:
- Negritas para términos importantes
- Listas para pasos/procedimientos
- Código inline para fórmulas matemáticas
- Secciones claramente diferenciadas
"""

    def generar_respuesta(self, pregunta: str, contexto: Dict = None) -> str:
        # Construir el prompt según el tipo de pregunta
        if contexto and not contexto.get("pregunta_general", True):
            # Pregunta sobre un cálculo específico
            prompt = self._construir_prompt_especifico(pregunta, contexto)
        else:
            # Pregunta general sobre el método
            prompt = self._construir_prompt_general(pregunta)

        # Llamar al modelo de OpenAI
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content.strip()

    def _construir_prompt_general(self, pregunta: str) -> str:
        return f"""
El usuario hizo la siguiente pregunta GENERAL sobre el método de Falsa Posición:
{pregunta}

Por favor responde:
1. Explicando el concepto solicitado de manera clara y precisa
2. Proporcionando ejemplos numéricos si es relevante
3. Incluyendo cualquier advertencia importante sobre el método
4. Usando Markdown para mejorar la legibilidad
"""

    def _construir_prompt_especifico(self, pregunta: str, contexto: Dict) -> str:
        return f"""
El usuario hizo una pregunta ESPECÍFICA sobre un cálculo de Falsa Posición:

Pregunta: {pregunta}

Datos del problema:
- Función: {contexto.get('funcion', 'No especificada')}
- Intervalo inicial: [{contexto.get('a', '?')}, {contexto.get('b', '?')}]
- Tolerancia: {contexto.get('tolerancia', 'No especificada')}
- Iteraciones máximas: {contexto.get('max_iteraciones', 'No especificadas')}
- Resultados: {contexto.get('resultado', 'No disponibles')}

Por favor:
1. Analiza la pregunta en el contexto de estos datos específicos
2. Explica cualquier patrón o anomalía en los resultados
3. Proporciona recomendaciones específicas para este caso
4. Relaciona con los conceptos teóricos cuando sea relevante
"""


# ==========================================
# ===== CHATBOT ELIMINACIÓN GAUSS =========
# ==========================================
class GaussEliminacionChatbot(MetodoNumericoChatbot):
    def __init__(self):
        super().__init__()
        self.system_message = """
Eres un experto en el método de Eliminación Gaussiana para resolver sistemas de ecuaciones lineales. 
Debes responder de dos formas según el contexto:

1. Para preguntas GENERALES (sin datos específicos):
- Explica los fundamentos teóricos del método
- Describe el algoritmo paso a paso
- Compara con otros métodos (Gauss-Jordan, LU)
- Explica pivoteo y estabilidad numérica
- Proporciona ejemplos ilustrativos

2. Para preguntas ESPECÍFICAS (con datos de un sistema concreto):
- Analiza la matriz aumentada proporcionada
- Explica cada paso de eliminación con detalles
- Evalúa la elección de pivotes
- Detecta problemas numéricos o singularidades
- Sugiere mejoras para el caso específico

Usa Markdown para formatear tus respuestas con:
- Negritas para términos importantes
- Tablas para mostrar matrices
- Código inline para operaciones elementales
- Secciones claramente diferenciadas
"""

    def generar_respuesta(self, pregunta: str, contexto: Dict = None) -> str:
        if contexto and not contexto.get("pregunta_general", True):
            prompt = self._construir_prompt_especifico(pregunta, contexto)
        else:
            prompt = self._construir_prompt_general(pregunta)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        return response.choices[0].message.content.strip()

    def _construir_prompt_general(self, pregunta: str) -> str:
        return f"""
El usuario hizo la siguiente pregunta GENERAL sobre Eliminación Gaussiana:
{pregunta}

Por favor responde:
1. Explicando el concepto solicitado con profundidad matemática
2. Describiendo el algoritmo completo con complejidad O(n³)
3. Incluyendo ejemplos de sistemas 3x3 ilustrativos
4. Discutiendo ventajas/limitaciones del método
5. Mencionando variantes (pivoteo completo/parcial)
"""

    def _construir_prompt_especifico(self, pregunta: str, contexto: Dict) -> str:
        matriz_str = "\n".join(
            [
                "| " + " ".join(map(str, fila)) + " |"
                for fila in contexto.get("matriz", [])
            ]
        )

        return f"""
El usuario hizo una pregunta ESPECÍFICA sobre un sistema lineal:

Pregunta: {pregunta}

Datos del problema:
- Sistema: {contexto.get('sistema', 'No especificado')}
- Matriz aumentada:
{matriz_str}
- Tolerancia: {contexto.get('tolerancia', '1e-10')}
- Estrategia de pivoteo: {contexto.get('pivoteo', 'Parcial')}
- Resultados intermedios: {contexto.get('pasos', 'No disponibles')}

Por favor:
1. Analiza la matriz y detecta posibles problemas
2. Explica cada operación de fila realizada
3. Evalúa la estabilidad numérica del proceso
4. Calcula el error residual si es posible
5. Sugiere mejoras para este caso particular
"""

    def formatear_matriz(self, matriz):
        """Helper para formatear matrices legibles"""
        return (
            "\n".join(
                [
                    "| "
                    + " ".join(
                        f"{x:8.3f}" if isinstance(x, (int, float)) else f"{x:>8}"
                        for x in fila
                    )
                    + " |"
                    for fila in matriz
                ]
            )
            if matriz
            else "Matriz no proporcionada"
        )

    def generar_analisis_completo(self, problema: Dict) -> str:
        """Método alternativo para análisis estructurado"""
        analisis = [
            "## Análisis de Eliminación Gaussiana",
            f"**Sistema:** {problema.get('sistema', 'No especificado')}",
            "",
            "### Matriz Inicial",
            self.formatear_matriz(problema.get("matriz_inicial")),
            "",
            "### Proceso de Eliminación",
        ]

        for i, paso in enumerate(problema.get("pasos", []), 1):
            analisis.extend(
                [
                    f"\n**Paso {i}:** {paso.get('descripcion', '')}",
                    f"- Pivote: {paso.get('pivote', 'N/A')}",
                    f"- Operación: {paso.get('operacion', '')}",
                    self.formatear_matriz(paso.get("matriz_intermedia")),
                    f"_Observación:_ {paso.get('observacion', '')}",
                ]
            )

        analisis.extend(
            [
                "\n### Resultados Finales",
                f"Solución: {problema.get('solucion', 'No calculada')}",
                f"Error residual: {problema.get('error', 'N/A')}",
                f"Condición numérica: {problema.get('condicion', 'N/A')}",
                "",
                "### Recomendaciones",
                self._generar_recomendaciones(problema),
            ]
        )

        return "\n".join(analisis)

    def _generar_recomendaciones(self, problema: Dict) -> str:
        recs = []
        matriz = problema.get("matriz_inicial", [])

        if len(matriz) > 10:
            recs.append("✅ Para matrices grandes considere métodos iterativos")

        if problema.get("pivoteo") != "Completo":
            recs.append(
                "⚠️ Matriz con posibles problemas de estabilidad - Use pivoteo completo"
            )

        if any(abs(x) < 1e-5 for fila in matriz for x in fila):
            recs.append("🔍 Valores muy pequeños detectados - Considere escalamiento")

        return "\n".join(recs) if recs else "El proceso parece óptimo para este caso"


# ==========================================
# ===== CHATBOT GAUSS-JORDAN ==============
# ==========================================
class GaussJordanChatbot(MetodoNumericoChatbot):
    def __init__(self):
        super().__init__()
        self.system_message = """
Eres un experto en el método de Gauss-Jordan para resolver sistemas de ecuaciones lineales.
Responde según el contexto:

1. Para preguntas GENERALES:
- Explica los fundamentos teóricos
- Muestra el algoritmo paso a paso
- Compara con otros métodos como Eliminación de Gauss o LU
- Ejemplifica con sistemas 3x3
- Analiza ventajas y limitaciones

2. Para preguntas ESPECÍFICAS:
- Interpreta la matriz aumentada proporcionada
- Explica las operaciones de fila realizadas
- Muestra cada paso de la reducción a RREF
- Detecta soluciones únicas, infinitas o inconsistencias
- Proporciona la solución final

Utiliza Markdown:
- **Negritas** para conceptos clave
- Tablas para matrices
- Código inline para operaciones elementales
- Secciones diferenciadas
"""

    def generar_respuesta(self, pregunta: str, contexto: Dict = None) -> str:
        prompt = (
            self._construir_prompt_especifico(pregunta, contexto)
            if contexto and not contexto.get("pregunta_general", True)
            else self._construir_prompt_general(pregunta)
        )

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        return response.choices[0].message.content.strip()

    def _construir_prompt_general(self, pregunta: str) -> str:
        return f"""
El usuario hizo una pregunta GENERAL sobre el método de Gauss-Jordan:

{pregunta}

Responde incluyendo:
1. Concepto de forma escalonada reducida (RREF)
2. Algoritmo paso a paso con ejemplos de operaciones elementales
3. Comparación con otros métodos como Eliminación de Gauss
4. Ejemplo con sistema 3x3
5. Ventajas y desventajas del método
"""

    def _construir_prompt_especifico(self, pregunta: str, contexto: Dict) -> str:
        matriz = contexto.get("matriz", [])
        matriz_str = self.formatear_matriz(matriz)
        clasificacion = contexto.get("clasificacion", "Desconocida")

        return f"""
El usuario hizo una pregunta ESPECÍFICA sobre un sistema lineal resuelto con Gauss-Jordan:

Pregunta: {pregunta}

Datos del sistema:
- Sistema: {contexto.get('sistema', 'No especificado')}
- Matriz aumentada inicial:
{matriz_str}
- Proceso aplicado: Forma escalonada reducida (RREF)
- Clasificación del sistema: {clasificacion}

Por favor responde:
1. Explica cada operación realizada en la matriz
2. Muestra el proceso hacia la forma RREF con claridad
3. Presenta la solución o determina si hay infinitas/no hay solución
4. Interpreta el resultado
"""

    def formatear_matriz(self, matriz: list) -> str:
        if not matriz:
            return "Matriz no proporcionada"

        return "\n".join(
            "| "
            + " ".join(
                f"{x:8.3f}" if isinstance(x, (int, float)) else f"{x:>8}" for x in fila
            )
            + " |"
            for fila in matriz
        )

    def generar_analisis_completo(self, problema: Dict) -> str:
        matriz_inicial = self.formatear_matriz(problema.get("matriz_inicial", []))
        pasos = problema.get("pasos", [])
        clasificacion = problema.get("clasificacion", "Desconocida")
        solucion = problema.get("solucion", "No calculada")

        analisis = [
            "## Análisis del Método de Gauss-Jordan",
            f"**Sistema:** {problema.get('sistema', 'No especificado')}",
            "",
            "### Matriz Inicial",
            matriz_inicial,
            "",
            "### Proceso de Reducción a RREF",
        ]

        for i, paso in enumerate(pasos, 1):
            analisis.extend(
                [
                    f"**Paso {i}:** {paso.get('descripcion', '')}",
                    f"- Operación: `{paso.get('operacion', '')}`",
                    self.formatear_matriz(paso.get("matriz_intermedia", [])),
                    f"_Observación:_ {paso.get('observacion', '')}",
                    "",
                ]
            )

        analisis.extend(
            [
                "### Resultado Final",
                f"**Solución:** {solucion}",
                f"**Clasificación:** {clasificacion}",
                "",
                "### Recomendaciones",
                self._generar_recomendaciones(problema),
            ]
        )

        return "\n".join(analisis)

    def _generar_recomendaciones(self, problema: Dict) -> str:
        matriz = problema.get("matriz_inicial", [])
        recs = []

        if len(matriz) > 10:
            recs.append(
                "✅ Para sistemas grandes, considere métodos iterativos como Jacobi o Gauss-Seidel."
            )

        if any(abs(x) < 1e-6 for fila in matriz for x in fila):
            recs.append(
                "🔍 Hay elementos muy pequeños en la matriz. Considere usar pivoteo parcial o escalamiento."
            )

        if problema.get("clasificacion") == "Sistema inconsistente":
            recs.append("⚠️ El sistema es inconsistente. No tiene solución.")

        return (
            "\n".join(recs)
            if recs
            else "✅ Método adecuado aplicado correctamente al sistema dado."
        )


# ==========================================
# ===== CHATBOT DIFERENCIACIÓN FINITA =====
# ==========================================
class DiferenciasFinitasChatbot(MetodoNumericoChatbot):
    def __init__(self):
        super().__init__()
        self.system_message = """
Eres un experto en métodos de Diferencias Finitas para aproximación de derivadas.
Responde de dos formas:

1. Preguntas GENERALES:
- Explica diferencias hacia adelante, atrás y centradas
- Analiza orden de error y precisión
- Da ejemplos sencillos con funciones conocidas
- Compara métodos y recomienda tamaños de h

2. Preguntas ESPECÍFICAS (con valores de f(x), h, x):
- Muestra los resultados de cada método de forma clara
- Comenta el error y precisión observada
- Sugiere si conviene un h mayor o menor
"""

    def generar_respuesta(self, pregunta: str, contexto: Dict = None) -> str:
        if contexto and not contexto.get("pregunta_general", True):
            prompt = self._construir_prompt_especifico(pregunta, contexto)
        else:
            prompt = self._construir_prompt_general(pregunta)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content.strip()

    def _construir_prompt_general(self, pregunta: str) -> str:
        return f"""
Pregunta GENERAL sobre Diferencias Finitas:

{pregunta}

Por favor responde:
1. Explicando diferencias hacia adelante, atrás y centradas
2. Dando ejemplos con funciones como e^x, sin(x), ln(x)
3. Analizando el orden de error de cada fórmula
4. Comparando precisión entre métodos
5. Recomendando valores típicos de h
"""

    def _construir_prompt_especifico(self, pregunta: str, contexto: Dict) -> str:
        resumen_resultados = self._formatear_resumen(contexto)

        return f"""
Pregunta ESPECÍFICA sobre derivación numérica:

{pregunta}

Datos:
- Función evaluada: {contexto.get('funcion', 'No especificada')}
- Punto de evaluación: x = {contexto.get('x', '?')}
- Tamaño de paso: h = {contexto.get('h', '?')}

Resultados resumidos:

{resumen_resultados}

Por favor responde:
1. Explicando brevemente los cálculos y resultados
2. Comparando precisión entre los métodos usados
3. Sugerencias de mejora si es necesario
"""

    def _formatear_resumen(self, contexto: Dict) -> str:
        pasos = contexto.get("pasos", [])
        if not pasos:
            return "No se proporcionaron resultados."

        filas = "\n".join(
            f"- {p['metodo']}: derivada ≈ {p['resultado']:.6f} (error: {p.get('error', 'N/A')})"
            for p in pasos
        )
        return filas

    def generar_analisis_completo(self, problema: Dict) -> str:
        resumen = self._formatear_resumen(problema)
        recomendaciones = self._generar_recomendaciones(problema)

        return f"""
## Análisis de Diferencias Finitas

**Función:** {problema.get('funcion', 'No especificada')}
**Punto x:** {problema.get('x', '?')}
**h:** {problema.get('h', '?')}

### Resultados:

{resumen}

### Recomendaciones:

{recomendaciones}
"""

    def _generar_recomendaciones(self, problema: Dict) -> str:
        h = problema.get("h", 0.1)
        recs = []

        if h > 0.5:
            recs.append("⚠️ El paso h es grande, puede causar error de truncamiento.")
        elif h < 1e-4:
            recs.append("⚠️ h es muy pequeño, puede provocar error de redondeo.")

        if len(problema.get("metodos", [])) < 2:
            recs.append("✅ Prueba varios métodos para comparar precisión.")

        return "\n".join(recs) if recs else "✅ Elección adecuada de parámetros."


# ==========================================
# ===== CHATBOT INTERPOLACIÓN =============
# ==========================================
class InterpolacionChatbot(MetodoNumericoChatbot):
    def __init__(self):
        super().__init__()
        self.system_message = """
Eres un experto en métodos de Interpolación Numérica.
Debes responder de dos formas según el contexto:

1. Para preguntas GENERALES:
- Explica los fundamentos de los métodos (Lagrange, Newton, splines)
- Compara ventajas/desventajas entre métodos
- Describe cómo seleccionar puntos óptimos (Chebyshev, equidistantes)
- Analiza el fenómeno de Runge y cómo mitigarlo
- Muestra ejemplos simples con 3 o 4 puntos

2. Para preguntas ESPECÍFICAS:
- Interpreta los puntos dados y el grado del polinomio
- Explica cómo se construye el interpolante de forma clara pero resumida
- Da la fórmula final del polinomio si es posible
- Recomienda buenas prácticas para evitar errores numéricos
"""

    def generar_respuesta(self, pregunta: str, contexto: Dict = None) -> str:
        if contexto and not contexto.get("pregunta_general", True):
            prompt = self._construir_prompt_especifico(pregunta, contexto)
        else:
            prompt = self._construir_prompt_general(pregunta)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1200,
        )

        return response.choices[0].message.content.strip()

    def _construir_prompt_general(self, pregunta: str) -> str:
        return f"""
El usuario hizo la siguiente pregunta GENERAL sobre Interpolación Numérica:
{pregunta}

Por favor responde:
1. Explicando el fundamento del método (Newton, Lagrange, etc.)
2. Mostrando un ejemplo sencillo con 3 puntos
3. Describiendo cómo se construye el polinomio paso a paso
4. Analizando errores comunes (fenómeno de Runge, sobreajuste)
5. Comparando con otros métodos de interpolación
"""

    def _construir_prompt_especifico(self, pregunta: str, contexto: Dict) -> str:
        puntos = "\n".join(f"({p['x']}, {p['y']})" for p in contexto.get("puntos", []))
        resumen_pasos = self._resumir_pasos(contexto.get("pasos", []))
        polinomio = contexto.get("polinomio", "No proporcionado")

        return f"""
El usuario planteó una pregunta ESPECÍFICA sobre interpolación numérica.

Pregunta: {pregunta}

Método: {contexto.get('metodo', 'No especificado')}
Grado del polinomio: {contexto.get('grado', '?')}
Puntos a interpolar:
{puntos}

Resumen del cálculo:
{resumen_pasos}

Polinomio resultante:
{polinomio}

Por favor:
1. Explica cómo se construyó el interpolante de forma resumida
2. Analiza si los puntos están bien distribuidos
3. Da recomendaciones para evitar oscilaciones o errores numéricos
4. Evalúa la precisión o error esperado si es posible
"""

    def _resumir_pasos(self, pasos: List[Dict]) -> str:
        if not pasos:
            return "No se registraron pasos o el proceso fue directo."

        n = len(pasos)
        coeficientes = [str(p.get("coeficiente", "N/A")) for p in pasos]

        return (
            f"Se calcularon {n} coeficientes de diferencias divididas:\n"
            f"{', '.join(coeficientes)}"
        )

    def formatear_puntos(self, puntos: List[Dict]) -> str:
        if not puntos:
            return "Sin puntos especificados"
        return "\n".join([f"- ({p['x']}, {p['y']})" for p in puntos])

    def generar_analisis_completo(self, problema: Dict) -> str:
        # Esta función la dejamos para reportes detallados (PDF o logs), no para el chatbot rápido
        analisis = [
            "## Análisis del Método de Interpolación",
            f"**Método:** {problema.get('metodo', 'No especificado')}",
            f"**Grado del polinomio:** {problema.get('grado', '?')}",
            "",
            "### Puntos Utilizados",
            self.formatear_puntos(problema.get("puntos", [])),
            "",
            "### Coeficientes calculados",
        ]

        for i, paso in enumerate(problema.get("pasos", []), 1):
            analisis.extend(
                [
                    f"- Coeficiente {i}: {paso.get('coeficiente', 'N/A')} ({paso.get('termino', '')})",
                ]
            )

        analisis.extend(
            [
                "\n### Resultados Finales",
                f"Polinomio interpolante: {problema.get('polinomio', 'No calculado')}",
                f"Error estimado: {problema.get('error', 'N/A')}",
                "",
                "### Recomendaciones",
                self._generar_recomendaciones(problema),
            ]
        )

        return "\n".join(analisis)

    def _generar_recomendaciones(self, problema: Dict) -> str:
        puntos = problema.get("puntos", [])
        n = len(puntos)

        recs = []
        if n > 8:
            recs.append(
                "⚠️ Usar muchos puntos puede causar oscilaciones (Fenómeno de Runge). Considera usar **splines**."
            )
        if problema.get("metodo", "").lower() in ["lagrange", "newton"] and n >= 5:
            recs.append(
                "✅ Considera usar nodos de **Chebyshev** para mejorar la estabilidad."
            )
        if (
            problema.get("error", None)
            and isinstance(problema["error"], float)
            and problema["error"] > 0.01
        ):
            recs.append(
                "🔍 El error es relativamente alto. Revisa la distribución de los puntos o reduce el grado del polinomio."
            )

        return (
            "\n".join(recs)
            if recs
            else "✅ Método y puntos bien seleccionados para la interpolación."
        )


# ==========================================
# ===== FUNCIÓN UNIFICADA ==================
# ==========================================
def obtener_chatbot_metodo(metodo: str) -> Union[MetodoNumericoChatbot, None]:
    """Factory function para obtener el chatbot adecuado según el método"""
    metodo = metodo.lower().replace(" ", "_")

    if metodo == "falsa_posicion":
        return FalsaPosicionChatbot()
    elif metodo in ["gauss", "eliminacion_gaussiana"]:
        return GaussEliminacionChatbot()
    elif metodo == "gauss_jordan":
        return GaussJordanChatbot()
    elif metodo in ["diferenciacion", "diferencias_finitas"]:
        return DiferenciasFinitasChatbot()
    elif metodo == "interpolacion":
        return InterpolacionChatbot()
    else:
        return None


# ==========================================
# ===== MANTENER COMPATIBILIDAD ============
# ==========================================
# Las siguientes funciones mantienen compatibilidad con el código existente


def responder_pregunta_metodo(metodo: str, pregunta: str, contexto: Dict = None) -> str:
    chatbot = obtener_chatbot_metodo(metodo)
    if chatbot:
        return chatbot.generar_respuesta(pregunta, contexto)
    return f"Método '{metodo}' no soportado por el chatbot."
