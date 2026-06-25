> **Created:** 2026-06-24
> **Last Updated:** 2026-06-24

# Aprendizajes y Arquitectura: Motor Híbrido de Visualización (Sin IA)

Este documento registra las decisiones arquitectónicas, lecciones aprendidas y soluciones técnicas aplicadas durante el desarrollo de la herramienta de recomendación y generación de gráficos.

---

## 1. Decisiones de Arquitectura

### A. Uso de `ydata-profiling` en modo Headless (Sin Renderizado HTML)
*   **Decisión:** En lugar de implementar algoritmos de inferencia semántica y cálculos de skewness (sesgo), curtosis u outliers desde cero, decidimos envolver `ydata-profiling` (anteriormente `pandas-profiling`).
*   **Por qué:** Reinventar la rueda de la inferencia de tipos (especialmente para datos sucios con nulos) es altamente costoso y propenso a fallas. `ydata-profiling` integra la librería `visions`, que maneja de manera madura la clasificación semántica.
*   **Implementación:** Se inicializa `ProfileReport` en modo `minimal=True` para máxima velocidad en memoria y se extrae directamente el objeto de metadatos estructurados llamando a `.get_description()`, evitando el pesado proceso de renderizar su interfaz HTML nativa.

### B. Streamlit + Plotly Express como Capa de Interfaz y Diseño Premium
*   **Decisión:** Seleccionamos una arquitectura monolítica local en Python frente a un desarrollo SPA (React/Vite) + Backend (FastAPI).
*   **Por qué:** Python es el estándar de oro en procesamiento estadístico. Plotly Express permite una interactividad excepcional (zoom, hover, exportación vectorial) que se puede vestir de forma premium directamente desde código Python sin requerir sincronización de estados ni APIs complejas.

---

## 2. Gotchas Técnicos y Lecciones Aprendidas

### A. Estructura de `BaseDescription` frente a Diccionarios Estándar
*   **Problema:** El output de `.get_description()` en `ydata-profiling` 4.0+ no es un diccionario nativo, sino una instancia del objeto dataclass/pydantic `BaseDescription`. Intentar acceder mediante `.get("variables")` provoca un error de atributo (`AttributeError`).
*   **Solución:** Se accede a las claves principales directamente como propiedades del objeto (`desc.variables` y `desc.table`), las cuales sí contienen diccionarios estándar de Python de fácil iteración.

### B. Correlaciones Ausentes en Modo Minimal
*   **Problema:** Al activar `minimal=True` en `ydata-profiling` para acelerar el procesamiento, las matrices de correlación (Pearson, Spearman) se omiten por completo de la clave `correlations`.
*   **Solución:** Desacoplamos el cálculo de correlaciones del motor de profiling y lo ejecutamos directamente sobre el DataFrame de Pandas utilizando `df.corr(method="pearson", numeric_only=True)`. Esto es sumamente rápido y garantiza la disponibilidad de datos de correlación lineal en cualquier circunstancia.

### C. Variables Numéricas Discretas de Baja Cardinalidad
*   **Problema:** Columnas numéricas que representan categorías discretas (como códigos `[0, 1, 2]`) eran clasificadas como cuantitativas continuas, sugiriendo histogramas irrelevantes.
*   **Solución:** Implementamos una regla de coerción en `analyzer.py` que reclasifica columnas numéricas con una cardinalidad inferior a 10 valores únicos como de tipo `Nominal` (Categórica), forzando sugerencias más legibles como gráficos de barras o comparativas de medias.

### D. Ejecución de Streamlit en Windows
*   **Problema:** Al instalar dependencias en Windows, los binarios y ejecutables de Streamlit se guardan en la carpeta local de scripts de Python, la cual rara vez se encuentra registrada en la variable de entorno `PATH` del sistema, provocando fallas al ejecutar el comando global `streamlit`.
*   **Solución:** Ejecutar la aplicación de forma alternativa utilizando el comando de ejecución de módulos de Python: `python -m streamlit run app.py`.

---

## 3. Patrón de Despliegue Híbrido Coexistente

Uno de los principales aprendizajes del proyecto fue estructurar un **único repositorio de GitHub capaz de alimentar dos plataformas de nube gratuitas distintas sin interferir entre sí**:

1.  **Vercel (Estático):** Lee e implementa el archivo [index.html](file:///c:/Users/anaca/Repos/plot-this/index.html) de la raíz de forma gratuita, sirviendo un iframe de pantalla completa que enmascara el dominio personalizado de **Namecheap**.
2.  **Streamlit Community Cloud (Servidor Python):** Ignora el archivo estático HTML y ejecuta directamente [app.py](file:///c:/Users/anaca/Repos/plot-this/app.py) para levantar el backend de procesamiento de datos y gráficos interactivos.

Este patrón de diseño permite que el usuario tenga una experiencia de producto con dominio de marca profesional, libre de cargos de servidor y sin la sobrecarga de mantener múltiples repositorios.
