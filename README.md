# PlotThis 📊

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

[English](#english) | [Español](#español)

---

<a name="english"></a>
## English

### 1. Project Description
PlotThis is a local, privacy-focused interactive web application designed to analyze structured datasets, suggest the most appropriate chart types, and generate automated statistical insights in Spanish, without using Artificial Intelligence (AI) or third-party APIs. 

The application works as a hybrid system: it uses a highly-optimized, custom mathematical engine built purely in **`Pandas`** in the background to infer semantic types and compile summaries in milliseconds. It renders a custom interface using **`Streamlit`** and premium styled charts using **`Plotly Express`**.

### 2. Technologies Used
- **Language:** Python
- **Backend / Profiling Engine:** Pure Pandas (Native)
- **UI Framework:** Streamlit
- **Visualization:** Plotly Express
- **Scientific Computing:** Pandas, NumPy, SciPy
- **Hosting / Deployments:** Streamlit Community Cloud

### 3. Key Learnings
Building this application provided valuable experience in the following areas:
- **Streamlit Performance Optimization:** Discovered that heavy third-party data profiling libraries (like `ydata-profiling`) cause severe multiprocessing deadlocks and UI freezes in Streamlit's reactive environment. Replacing them with a custom engine using pure native Pandas methods (`df.corr()`, `df.skew()`) reduced analysis processing time from over 60 seconds (hanging) to 0.08 seconds.
- **Dynamic Bivariate Heuristics:** Implementing a deterministic rules engine that evaluates Pearson/Spearman coefficients and mean variances to recommend specific chart types, mimicking the strict design rules found in corporate systems like Tableau and Excel.
- **Aesthetic Customization of Plotly:** Fine-tuning Plotly layouts (Inter/Outfit typography, removing axis borders, applying custom color palettes, and formatting custom tooltips) to produce charts that look modern and publication-ready.

---

<a name="español"></a>
## Español

### 1. Descripción del Proyecto
PlotThis es una aplicación web interactiva local, enfocada en la privacidad, diseñada para analizar datasets estructurados, sugerir los tipos de gráficos más adecuados y generar insights estadísticos automáticos en español, sin recurrir a Inteligencia Artificial (IA) ni a APIs externas.

La aplicación funciona de forma híbrida: utiliza un motor matemático personalizado y altamente optimizado construido puramente en **`Pandas`** en segundo plano para inferir tipos semánticos y compilar métricas en milisegundos. Renderiza una interfaz interactiva personalizada mediante **`Streamlit`** y gráficos vectoriales premium con **`Plotly Express`**.

### 2. Tecnologías Utilizadas
- **Lenguaje:** Python
- **Motor de Profiling:** Pandas Puro (Nativo)
- **Framework de UI:** Streamlit
- **Visualización:** Plotly Express
- **Cálculo Científico:** Pandas, NumPy, SciPy
- **Despliegues:** Streamlit Community Cloud

### 3. Aprendizajes Destacados
La creación de esta aplicación me permitió profundizar en:
- **Optimización de Rendimiento en Streamlit:** Descubrir que el uso de librerías de profiling pesadas (como `ydata-profiling`) causan deadlocks de multiprocesamiento severos y cuelgues de UI en entornos reactivos de Streamlit. Reemplazar esto con un motor personalizado utilizando métodos nativos de Pandas (`df.corr()`, `df.skew()`) redujo el tiempo de procesamiento de más de 60 segundos (colapso) a tan solo 0.08 segundos.
- **Heurísticas Bivariantes Dinámicas:** Implementar un motor de reglas determinista que evalúa coeficientes de Pearson/Spearman y diferencias de medias para sugerir gráficos idóneos, replicando las reglas de diseño estructuradas de herramientas corporativas como Tableau y Excel.
- **Estilización Avanzada en Plotly:** Personalizar las propiedades del layout de Plotly Express (tipografía *Inter/Outfit*, eliminación de bordes de eje redundantes, uso de cuadrículas sutiles y paletas coordinadas) para producir gráficos con un acabado visual premium y moderno.
