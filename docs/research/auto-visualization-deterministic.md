> **Created:** 2026-06-24
> **Last Updated:** 2026-06-24

# Investigación: Recomendación Determinista de Visualizaciones de Datos

Este documento recopila la investigación sobre herramientas y metodologías deterministas (no basadas en IA/LLMs) que analizan datasets y proponen de forma automatizada los mejores gráficos.

---

## 1. Análisis Técnico de Herramientas Existentes en Python (Paso Extra)

A continuación, se detalla la lógica interna, el mecanismo de inferencia de tipos y los algoritmos que emplean las librerías líderes de código abierto para proponer gráficos sin el uso de Inteligencia Artificial:

### A. ydata-profiling (antes pandas-profiling)
*   **Mecanismo de Inferencia de Tipos:** Utiliza la librería **`visions`** como motor central. Esta librería supera el límite del tipo de almacenamiento físico de Pandas (`dtype` como `object` o `int64`) y modela un grafo de tipos semánticos (por ejemplo, identificando si una serie de texto contiene números correlativos o fechas y realizando una conversión semántica implícita).
*   **Algoritmo de Selección:** Genera reportes HTML completos basándose en la naturaleza del tipo detectado:
    *   *Univariante:* Si la columna es numérica (Quantitative), dibuja histogramas de distribución y analiza cuartiles y valores extremos. Si es categórica, calcula frecuencias absolutas y cardinalidad.
    *   *Correlaciones cruzadas:* Calcula automáticamente Pearson, Spearman, Kendall, Cramer's V (para variables nominales) y **$\phi_K$ (Phik)**, un coeficiente robusto para capturar asociaciones no lineales entre mezclas de variables numéricas y categóricas. Las correlaciones con mayor puntuación generan gráficos bivariantes automáticos.
*   **Código de uso estándar:**
    ```python
    from ydata_profiling import ProfileReport
    profile = ProfileReport(df, infer_dtypes=True)
    profile.to_file("reporte.html")
    ```

### B. Sweetviz
*   **Mecanismo de Inferencia de Tipos:** Clasifica de forma autónoma las variables en tres categorías: Numéricas, Categóricas y de Texto, basándose en la proporción de valores numéricos y la cardinalidad de los registros.
*   **Algoritmo de Selección:** Su fortaleza radica en el **análisis de variable objetivo (Target Analysis)**. Si el usuario define una columna de control (target), Sweetviz calcula automáticamente asociaciones univariantes y bivariantes cruzando cada variable del dataset contra la variable objetivo. Si la variable objetivo es binaria, genera diagramas de caja agrupados; si es continua, calcula curvas de correlación localmente suavizadas (LOESS) y distribuciones solapadas.
*   **Código de uso estándar:**
    ```python
    import sweetviz as sv
    report = sv.analyze(df, target_feat="variable_objetivo")
    report.show_html()
    ```

### C. AutoViz (de Abid Ali Awan)
*   **Mecanismo de Inferencia de Tipos:** Clasifica rápidamente columnas analizando el recuento de valores únicos. Por ejemplo, si una columna numérica contiene menos de 20 valores únicos, la reclasifica automáticamente como categórica (Nominal/Ordinal) para evitar gráficos continuos incoherentes.
*   **Algoritmo de Selección:** Utiliza una serie de heurísticas de rendimiento para evitar saturar al usuario:
    *   Si hay más de 10 variables numéricas, calcula la correlación y genera gráficos de dispersión (Scatter Plots) únicamente para los pares que superan cierto umbral de correlación, limitando el número total de gráficos a mostrar.
    *   Selecciona de forma automática entre diagramas de barras, histogramas, gráficos de caja (Box Plots) y diagramas de violín (para contrastar distribuciones numéricas según categorías) en base al número total de registros y columnas.
*   **Código de uso estándar:**
    ```python
    from autoviz.AutoViz_Class import AutoViz_Class
    AV = AutoViz_Class()
    dft = AV.AutoViz(filename="archivo.csv", sep=",", depVar="variable_objetivo")
    ```

### D. D-Tale
*   **Mecanismo de Inferencia de Tipos:** Utiliza un backend en Flask acoplado a un frontend en React. Mapea directamente los tipos de datos físicos del DataFrame a un diccionario de metadatos en JS.
*   **Algoritmo de Selección:** A diferencia de los generadores estáticos, D-Tale expone un creador de gráficos interactivo dinámico que **habilita/deshabilita opciones según la selección**:
    *   Si el usuario selecciona una sola columna cuantitativa, bloquea opciones complejas y sugiere un Histograma o Box Plot.
    *   Si selecciona 1 variable nominal y 1 cuantitativa, habilita gráficos de barras agregando la métrica (promedio, suma, mediana) o histogramas segmentados.
*   **Código de uso estándar:**
    ```python
    import dtale
    d = dtale.show(df)
    d.open_browser()
    ```

### E. Lux (La experiencia de recomendación más avanzada)
*   **Mecanismo de Inferencia de Tipos:** Analiza el DataFrame e infiere tipos semánticos en base al rango de los valores y nombres de columna comunes (ej. fechas).
*   **Algoritmo de Selección (Interestingness Scoring):** Es el sistema más avanzado de reglas estadísticas sin IA. Su motor evalúa el interés de los gráficos basándose en las siguientes heurísticas de ordenamiento:
    *   *Para gráficos de líneas y barras (sin filtros):* Calcula la **Desigualdad/Asimetría (Unevenness)** midiendo la distancia euclidiana (L2 norm) entre la distribución observada y una distribución uniforme (plana). Cuanto más irregular sea la distribución, mayor es la puntuación de interés.
    *   *Para gráficos con filtros aplicados:* Mide la **Desviación del Total (Deviation from Overall)** comparando la distribución del subconjunto contra la del dataset general mediante distancias L2 escaladas.
    *   *Para gráficos de dispersión (Scatter Plots):* Mide la **Monotonicidad** para priorizar y sugerir aquellos pares de variables numéricas que presentan una tendencia constante y lineal.
*   **Código de uso estándar:**
    ```python
    import lux
    import pandas as pd
    df = pd.read_csv("data.csv")
    df  # El output en Jupyter muestra una pestaña interactiva con las sugerencias anteriores
    ```

---

## 2. Herramientas Web Deterministas Existentes

Estas aplicaciones en la nube analizan la estructura de datos para determinar visualizaciones sin recurrir a procesamiento de lenguaje natural o IA:

### A. LiveGap Charts
*   **Qué hace:** Habilita de forma proactiva plantillas de gráficos compatibles en su panel al pegar un dataset plano.
*   **Lógica:** Analiza si el formato pegado corresponde a una tabla unidimensional, bidimensional o de series temporales, bloqueando las opciones visuales incompatibles (por ejemplo, deshabilita gráficos de dispersión si no detecta al menos dos series numéricas).
*   **Enlace:** [LiveGap Charts](https://charts.livegap.com/)

### B. Chartle.es
*   **Qué hace:** Genera la gráfica de inmediato en base a un asistente interactivo y permite conmutar entre formatos de renderizado.
*   **Lógica:** Validación estructurada de campos de entrada utilizando restricciones duras por gráfico (ej. los gráficos de radar exigen múltiples dimensiones pero con una sola métrica).

---

## 3. Lógica de Recomendación en Herramientas Corporativas Clásicas

Las suites de Business Intelligence y hojas de cálculo utilizan motores de decisión deterministas basados en reglas de visualización tradicionales:

*   **Excel y Google Sheets ("Gráficos recomendados"):** El software evalúa la orientación del dataset (horizontal/vertical) y la presencia de cabeceras. Si detecta una columna de tipo fecha a la izquierda y valores continuos a la derecha, prioriza el gráfico de líneas. Si la columna izquierda contiene texto con baja cardinalidad, sugiere un gráfico de barras.
*   **Tableau Public ("Show Me" / "Mostrar"):** Implementa el motor de reglas de visualización más rígido y robusto de la industria. Cada tipo de gráfico tiene requisitos de dimensiones y medidas mínimos y máximos:
    *   *Mapa de símbolos:* Requiere 1 campo geográfico, 0 o más dimensiones y de 0 a 2 medidas.
    *   *Scatter Plot:* Requiere exactamente 0 o más dimensiones y entre 2 y 4 medidas.
*   **Power BI:** Utiliza la inferencia del esquema de la base de datos local y relaciones declaradas en el modelo estrella para generar el gráfico inicial por defecto al arrastrar columnas al lienzo de trabajo.

---

## 4. 🧪 El Vacío Tecnológico / Oportunidad (¿Qué NO existe sin IA?)

Al contrastar estas herramientas, se identifica una clara oportunidad de desarrollo:

> **No existe una herramienta liviana de código abierto ejecutada enteramente en la web (Client-Side) que tome un archivo CSV plano del usuario y aplique pruebas estadísticas de distribución y correlación locales para proponer una lista clasificada de gráficos (incluyendo análisis de outliers, box plots explicados, treemaps e histogramas óptimos) sin comprometer la privacidad de los datos.**

Las herramientas de Python (como Lux o Profiling) requieren conocimientos de programación y servidores locales Jupyter. Las herramientas como Excel o Tableau son aplicaciones de pago muy pesadas. Y las alternativas de IA modernas exigen subir información confidencial a la nube.

---

## 5. Diseño del Flujo Lógico y Heurísticas para nuestra Herramienta

Implementaremos esta arquitectura de manera modular en JavaScript:

### Inferencia de Tipos Semánticos
Nuestros algoritmos analizarán las primeras 100 filas de cada columna en el CSV:
1.  **Temporal (T):** Si al menos el 80% de los valores no vacíos superan la prueba de parseo de fecha (`!isNaN(Date.parse(val))` y coinciden con patrones comunes como `YYYY-MM-DD` o marcas temporales).
2.  **Quantitative (Q):** Si al menos el 90% de los valores se pueden convertir a número (`!isNaN(Number(val))`).
    *   *Subclasificación:* Si la columna cuantitativa posee una cardinalidad $< 10$, se marca como categórica ordinal para habilitar agregaciones rápidas.
3.  **Nominal (N):** Cadenas de texto que no califican como numéricas ni de fecha.

### Matriz de Decisiones de Recomendación

| Tipo de Datos | Métrica Estadística Clave | Gráfico Sugerido | Lógica y Criterio Técnico |
| :--- | :--- | :--- | :--- |
| **1 Q** | Curtosis y Sesgo de distribución | **Histograma** y **Box Plot** | Muestra la distribución. Si el sesgo es muy pronunciado ($|Sesgo| > 1$), se añade una nota explicando la asimetría de la muestra. |
| **1 N** | Cardinalidad (Valores únicos) | **Gráfico de Barras** | Si la cardinalidad es $\le 10$, barras verticales estándar. Si es entre 11 y 25, barras horizontales con scroll. Si es $> 25$, sugiere agrupar el excedente en "Otros". |
| **2 Q** | Coeficiente de Pearson ($r$) | **Scatter Plot** | Si hay correlación lineal moderada/alta ($|r| \ge 0.35$). Se calcula y grafica la recta de regresión lineal por mínimos cuadrados ($y = mx + b$). |
| **1 T + 1 Q** | Intervalo de tiempo constante | **Gráfico de Líneas** | Representa la evolución temporal del valor cuantitativo. |
| **1 N + 1 Q** | Varianza entre grupos | **Barras Agrupadas (Medias)** | Agrupa la variable numérica calculando el promedio para cada categoría nominal. |
| **2 N** | Conteo cruzado de categorías | **Mapa de Calor de Contingencia** | Matriz cruzada de frecuencias relativas. |
