import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import analyzer
import recommender
import styles

# Helper function to convert local image to base64 for HTML integration
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_error_card(msg):
    st.markdown(f'<div class="error-card">⚠️ {msg}</div>', unsafe_allow_html=True)

def render_warning_card(msg):
    st.markdown(f'<div class="warning-card">⚠️ {msg}</div>', unsafe_allow_html=True)

# Page setup and custom configurations using the local PNG file as the browser tab icon
st.set_page_config(
    page_title="PlotThis | Chart Recommender & Sugerencias de Gráficos",
    page_icon="plot-this-icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection for Outfit/Inter typography, card margins, and glassmorphic designs
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
    }
    
    .main-title-text {
        background: linear-gradient(90deg, #8C7AE6 0%, #5FAEE3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Hide native Streamlit deploy button for clean branding look */
    .stDeployButton {
        visibility: hidden;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: var(--text-color, #718096);
        margin-bottom: 2rem;
    }
    
    .card {
        background-color: var(--background-color, #FFFFFF);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--secondary-background-color, #E2E8F0);
        color: var(--text-color, #31333F);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
        height: 100%;
    }
    
    .card h4 {
        margin-top: 0;
        margin-bottom: 0.75rem;
    }
    
    .card p {
        margin-top: 0;
        margin-bottom: 0;
    }
    
    .insight-card {
        background-color: var(--secondary-background-color, #F8F9FA);
        border-radius: 12px;
        padding: 1.25rem;
        border-left: 5px solid #2C4D82;
        height: 100%;
    }
    
    .insight-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        color: #2C4D82;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .insight-text {
        font-size: 0.95rem;
        color: var(--text-color, #4A5568);
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .error-card {
        background-color: var(--secondary-background-color, #FFF5F5);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid #E53E3E;
        color: var(--text-color, #31333F);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }

    .warning-card {
        background-color: var(--secondary-background-color, #FFFFF0);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid #DD6B20;
        color: var(--text-color, #31333F);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #2C4D82;
    }
</style>
""", unsafe_allow_html=True)

# Translation dictionary for bilingual support (Spanish and English)
T = {
    "es": {
        "page_title": "PlotThis | Recomendador de Gráficos",
        "app_title": "PlotThis",
        "subtitle": "Sugerencia y generación de gráficos premium basados en análisis estadístico determinista",
        "config": "Configuración",
        "language": "Idioma / Language",
        "palette": "Paleta de Colores Visual",
        "upload_section": "Cargar Dataset",
        "upload_label": "Sube un archivo CSV o Excel",
        "upload_help": "El archivo debe contener al menos una columna numérica y cabeceras en la primera fila.",
        "error_read": "Error al leer el archivo",
        "column_types": "Modificar Tipos de Columna",
        "column_types_help": "Modifica la inferencia automática si consideras que es incorrecta:",
        "welcome_1_title": "100% Determinista",
        "welcome_1_text": "No usamos modelos de lenguaje (LLM). Las sugerencias e insights se derivan de coeficientes reales (Pearson, IQR, ANOVA) y reglas de visualización de Tableau y Excel.",
        "welcome_2_title": "Privacidad Total",
        "welcome_2_text": "El motor estadístico y de renderizado se ejecutan localmente en tu ordenador. Tus datos nunca viajan por internet ni son compartidos.",
        "welcome_3_title": "Visualizaciones Premium",
        "welcome_3_text": "Gráficos limpios con Plotly, fuentes Inter, rejillas minimalistas y paletas diseñadas para reportes listos para presentar.",
        "welcome_info": "Para comenzar, arrastra y suelta un archivo CSV o Excel en el panel izquierdo.",
        "tab_recs": "Gráficos Recomendados",
        "tab_manual": "Explorador Manual",
        "tab_data": "Vista de Datos",
        "recs_title": "Sugerencias del Motor Estadístico",
        "recs_subtitle": "Recomendaciones jerarquizadas automáticamente en base a correlaciones e indicadores detectados.",
        "no_recs": "No se pudieron generar sugerencias. Asegúrate de que el dataset contenga columnas numéricas o categóricas limpias.",
        "render_error": "No se pudo renderizar este tipo de gráfico.",
        "render_crit_error": "Error crítico al renderizar",
        "insight_title": "Insight Estadístico",
        "dataset_details": "Detalles del Dataset",
        "manual_title": "Construye tu propio gráfico",
        "manual_subtitle": "Selecciona las columnas y forzaremos las sugerencias basándonos en sus tipos y características estadísticas.",
        "axis_x": "Eje X (Variable principal)",
        "axis_y": "Eje Y (Variable de comparación)",
        "color_seg": "Segmentar por Color (Categórico)",
        "none": "Ninguno",
        "compat_warning": "Esta combinación de tipos de columna no está soportada o no es habitual para visualizaciones estándar.",
        "suggested_chart_type": "Tipo de Gráfico Sugerido",
        "manual_stats_title": "Estadísticas de Selección",
        "var_x": "Variable X",
        "var_y": "Variable Y",
        "bivariate_analysis": "Análisis Bivariante",
        "no_bivariate_detected": "No se detectaron correlaciones o desviaciones lineales notables entre este par de variables.",
        "data_preview_title": "Vista previa del Dataset",
        "data_preview_subtitle": "Mostrando las primeras 100 filas de",
        "summary_table_title": "Tabla resumen de Columnas e Inferencia",
        "summary_col": "Columna",
        "summary_inferred": "Tipo Inferido",
        "summary_orig": "Tipo Original (ydata)",
        "summary_unique": "Categorías Únicas",
        "summary_null": "Valores Nulos",
        "developed_by": "Desarrollado por",
    },
    "en": {
        "page_title": "PlotThis | Chart Recommender",
        "app_title": "PlotThis",
        "subtitle": "Premium chart suggestion and generation based on deterministic statistical analysis",
        "config": "Settings",
        "language": "Idioma / Language",
        "palette": "Visual Color Palette",
        "upload_section": "Upload Dataset",
        "upload_label": "Upload a CSV or Excel file",
        "upload_help": "The file must contain at least one numeric column and headers in the first row.",
        "error_read": "Error reading the file",
        "column_types": "Modify Column Types",
        "column_types_help": "Modify automatic inference if you consider it incorrect:",
        "welcome_1_title": "100% Deterministic",
        "welcome_1_text": "We do not use language models (LLMs). Suggestions and insights are derived from real coefficients (Pearson, IQR, ANOVA) and visualization rules from Tableau and Excel.",
        "welcome_2_title": "Total Privacy",
        "welcome_2_text": "The statistical and rendering engine runs locally on your computer. Your data never travels over the internet nor is it shared.",
        "welcome_3_title": "Premium Visualizations",
        "welcome_3_text": "Clean charts with Plotly, Inter fonts, minimalist grids, and palettes designed for presentation-ready reports.",
        "welcome_info": "To start, drag and drop a CSV or Excel file into the left panel.",
        "tab_recs": "Recommended Charts",
        "tab_manual": "Manual Explorer",
        "tab_data": "Data View",
        "recs_title": "Statistical Engine Suggestions",
        "recs_subtitle": "Recommendations automatically ranked based on detected correlations and indicators.",
        "no_recs": "No suggestions could be generated. Make sure the dataset contains clean numerical or categorical columns.",
        "render_error": "Could not render this chart type.",
        "render_crit_error": "Critical rendering error",
        "insight_title": "Statistical Insight",
        "dataset_details": "Dataset Details",
        "manual_title": "Build your own chart",
        "manual_subtitle": "Select columns and we will force suggestions based on their types and statistical characteristics.",
        "axis_x": "X Axis (Primary variable)",
        "axis_y": "Y Axis (Comparison variable)",
        "color_seg": "Segment by Color (Categorical)",
        "none": "None",
        "compat_warning": "This combination of column types is not supported or not standard for standard visualizations.",
        "suggested_chart_type": "Suggested Chart Type",
        "manual_stats_title": "Selection Statistics",
        "var_x": "Variable X",
        "var_y": "Variable Y",
        "bivariate_analysis": "Bivariate Analysis",
        "no_bivariate_detected": "No notable correlations or linear deviations were detected between this pair of variables.",
        "data_preview_title": "Dataset Preview",
        "data_preview_subtitle": "Showing the first 100 rows of",
        "summary_table_title": "Columns and Inference Summary Table",
        "summary_col": "Column",
        "summary_inferred": "Inferred Type",
        "summary_orig": "Original Type (ydata)",
        "summary_unique": "Unique Categories",
        "summary_null": "Null Values",
        "developed_by": "Developed by",
    }
}

# Initialize session state variables to cache dataframe computations and overrides
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.analysis = None
    st.session_state.metadata = None
    st.session_state.bivariate_insights = None
    st.session_state.file_name = ""
    st.session_state.lang_code = "es"

@st.cache_data(show_spinner="Analizando estructura y estadísticas con ydata-profiling...")
def run_dataset_profiling(df):
    return analyzer.analyze_dataset(df)

# Sidebar - Uploaders and configuration selectors
with st.sidebar:
    st.markdown("### Configuración / Settings")
    
    # Language Selector
    lang_selection = st.selectbox(
        "Idioma / Language",
        options=["Español", "English"],
        index=0
    )
    lang_code = "es" if lang_selection == "Español" else "en"
    
    # Handle language state change reactive flow
    lang_changed = False
    if "lang_code" in st.session_state and st.session_state.lang_code != lang_code:
        st.session_state.lang_code = lang_code
        lang_changed = True
    else:
        st.session_state.lang_code = lang_code
        
    if lang_changed and st.session_state.analysis is not None:
        # Re-extract and translate metadata and bivariate insights
        st.session_state.metadata = analyzer.extract_metadata(st.session_state.analysis, lang=lang_code)
        st.session_state.bivariate_insights = analyzer.calculate_bivariate_insights(
            st.session_state.df, 
            st.session_state.metadata, 
            st.session_state.analysis, 
            lang=lang_code
        )
    
    # Palette Theme Selector
    selected_theme = st.selectbox(
        T[lang_code]["palette"],
        options=["PlotThis Brand (Claro)", "PlotThis Brand (Oscuro)", "Classic Navy", "Cyberpunk (Dark)", "Warm Earth"],
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"### {T[lang_code]['upload_section']}")
    uploaded_file = st.file_uploader(
        T[lang_code]["upload_label"],
        type=["csv", "xlsx", "xls"],
        help=T[lang_code]["upload_help"]
    )
    
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.file_name:
            try:
                # Load file depending on file extension
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.df = df
                st.session_state.file_name = uploaded_file.name
                
                # Execute profiling logic
                desc = run_dataset_profiling(df)
                st.session_state.analysis = desc
                st.session_state.metadata = analyzer.extract_metadata(desc, lang=lang_code)
                st.session_state.bivariate_insights = analyzer.calculate_bivariate_insights(df, st.session_state.metadata, desc, lang=lang_code)
                
            except Exception as e:
                render_error_card(f"{T[lang_code]['error_read']}: {e}")
                
    # Show Column Type Modifier if metadata exists in session
    if st.session_state.metadata is not None:
        st.markdown("---")
        with st.expander(f"⚙️ {T[lang_code]['column_types']}"):
            st.caption(T[lang_code]['column_types_help'])
            
            updated_metadata = st.session_state.metadata.copy()
            types_changed = False
            
            for col, meta in st.session_state.metadata.items():
                current_type = meta["type"]
                options = ["Quantitative", "Nominal", "Temporal"]
                try:
                    selected_idx = options.index(current_type)
                except ValueError:
                    selected_idx = 1 # Nominal default fallback
                    
                new_type = st.selectbox(
                    f"{T[lang_code]['summary_col']}: {col}",
                    options=options,
                    index=selected_idx,
                    key=f"type_select_{col}"
                )
                
                if new_type != current_type:
                    updated_metadata[col]["type"] = new_type
                    types_changed = True
                    
            if types_changed:
                st.session_state.metadata = updated_metadata
                # Re-calculate bivariate insights based on modified metadata types and selected language
                st.session_state.bivariate_insights = analyzer.calculate_bivariate_insights(
                    st.session_state.df, 
                    updated_metadata, 
                    st.session_state.analysis,
                    lang=lang_code
                )

# Load and encode local icon in Base64 for the title layout
icon_src = ""
try:
    icon_b64 = get_base64_image("plot-this-icon.png")
    icon_src = f"data:image/png;base64,{icon_b64}"
    title_html = (
        f'<div class="main-title">'
        f'<img src="{icon_src}" style="height: 48px; vertical-align: middle; margin-right: 14px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.08);">'
        f'<span class="main-title-text">PlotThis</span>'
        f'</div>'
    )
except Exception:
    # Failback to plain text title if icon loading errors out
    title_html = '<div class="main-title"><span class="main-title-text">PlotThis</span></div>'

# Main Body UI layout
st.markdown(title_html, unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{T[lang_code]["subtitle"]}</div>', unsafe_allow_html=True)

if st.session_state.df is None:
    # Welcome Layout shown when no file is uploaded
    st.info(T[lang_code]["welcome_info"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="card" style="height: 100%;"><h4>{T[lang_code]["welcome_1_title"]}</h4><p style="color: var(--text-color, #718096); font-size: 0.9rem;">{T[lang_code]["welcome_1_text"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="card" style="height: 100%;"><h4>{T[lang_code]["welcome_2_title"]}</h4><p style="color: var(--text-color, #718096); font-size: 0.9rem;">{T[lang_code]["welcome_2_text"]}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card" style="height: 100%;"><h4>{T[lang_code]["welcome_3_title"]}</h4><p style="color: var(--text-color, #718096); font-size: 0.9rem;">{T[lang_code]["welcome_3_text"]}</p></div>', unsafe_allow_html=True)
else:
    # Navigation tabs
    tab_recs, tab_manual, tab_data = st.tabs([
        T[lang_code]["tab_recs"], 
        T[lang_code]["tab_manual"], 
        T[lang_code]["tab_data"]
    ])
    
    # ── TAB 1: CHART RECOMMENDATIONS ─────────────────────────────────────────────
    with tab_recs:
        st.markdown(f"### {T[lang_code]['recs_title']}")
        st.caption(T[lang_code]['recs_subtitle'])
        
        recs = recommender.recommend_charts(st.session_state.metadata, st.session_state.bivariate_insights, lang=lang_code)
        
        if not recs:
            render_warning_card(T[lang_code]["no_recs"])
        else:
            for idx, rec in enumerate(recs):
                chart_type = rec["chart_type"]
                x_col = rec["x"]
                y_col = rec["y"]
                color_by = rec["color_by"]
                title = rec["title"]
                
                # Split display container: Plotly figure on left, Insights text card on right
                with st.container():
                    col_chart, col_insight = st.columns([2, 1])
                    
                    with col_chart:
                        try:
                            fig = None
                            
                            # Render Plotly chart based on recommendation type
                            if chart_type == "scatter":
                                fig = px.scatter(
                                    st.session_state.df, 
                                    x=x_col, 
                                    y=y_col, 
                                    trendline="ols",
                                    trendline_color_override=styles.PALETTES[selected_theme]["accent"]
                                )
                            elif chart_type == "line":
                                fig = px.line(st.session_state.df, x=x_col, y=y_col)
                            elif chart_type == "histogram":
                                fig = px.histogram(st.session_state.df, x=x_col)
                            elif chart_type == "boxplot":
                                fig = px.box(st.session_state.df, y=x_col)
                            elif chart_type == "boxplot_segmented":
                                fig = px.box(st.session_state.df, x=x_col, y=y_col, color=color_by)
                            elif chart_type == "bar_aggregation":
                                agg_df = st.session_state.df.groupby(x_col)[y_col].mean().reset_index()
                                fig = px.bar(agg_df, x=x_col, y=y_col, color=color_by)
                            elif chart_type == "bar_frequency":
                                counts = st.session_state.df[x_col].value_counts().reset_index()
                                counts.columns = [x_col, "Frecuencia" if lang_code == "es" else "Frequency"]
                                fig = px.bar(counts, x=x_col, y="Frecuencia" if lang_code == "es" else "Frequency")
                            elif chart_type == "bar_horizontal":
                                counts = st.session_state.df[x_col].value_counts().reset_index()
                                counts.columns = [x_col, "Frecuencia" if lang_code == "es" else "Frequency"]
                                if len(counts) > 15:
                                    counts = counts.head(15)
                                    title += " (Top 15)"
                                fig = px.bar(counts, x="Frecuencia" if lang_code == "es" else "Frequency", y=x_col, orientation="h")
                                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                            elif chart_type == "pie":
                                counts = st.session_state.df[x_col].value_counts().reset_index()
                                counts.columns = [x_col, "Proporción" if lang_code == "es" else "Proportion"]
                                fig = px.pie(counts, names=x_col, values="Proporción" if lang_code == "es" else "Proportion")
                                
                            if fig is not None:
                                fig = styles.apply_premium_style(fig, title, selected_theme)
                                st.plotly_chart(fig, use_container_width=True, key=f"rec_chart_{idx}")
                            else:
                                render_error_card(T[lang_code]["render_error"])
                                
                        except Exception as e:
                            try:
                                if chart_type == "scatter":
                                    fig = px.scatter(st.session_state.df, x=x_col, y=y_col)
                                    fig = styles.apply_premium_style(fig, title, selected_theme)
                                    st.plotly_chart(fig, use_container_width=True, key=f"rec_chart_fb_{idx}")
                                else:
                                    render_error_card(f"{T[lang_code]['render_error']}: {e}")
                            except Exception as ex:
                                render_error_card(f"{T[lang_code]['render_crit_error']}: {ex}")
                                
                    with col_insight:
                        st.markdown(f"""
                        <div class="insight-card">
                            <div class="insight-title">{T[lang_code]["insight_title"]}</div>
                            <p class="insight-text">{rec['rationale']}</p>
                            <hr style="border: 0; border-top: 1px solid var(--secondary-background-color, #E2E8F0); margin: 1rem 0;">
                            <div style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: var(--text-color, #718096); letter-spacing: 0.05em; margin-bottom: 0.5rem;">{T[lang_code]["dataset_details"]}</div>
                            <ul style="padding-left: 1.1rem; font-size: 0.9rem; color: var(--text-color, #4A5568);">
                                {"".join(f"<li style='margin-bottom: 0.4rem;'>{ins}</li>" for ins in rec['insights'])}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

    # ── TAB 2: MANUAL EXPLORER ───────────────────────────────────────────────────
    with tab_manual:
        st.markdown(f"### {T[lang_code]['manual_title']}")
        st.caption(T[lang_code]['manual_subtitle'])
        
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        
        with col_sel1:
            x_manual = st.selectbox(
                T[lang_code]["axis_x"],
                options=st.session_state.df.columns.tolist(),
                index=0
            )
        with col_sel2:
            y_options = [T[lang_code]["none"]] + st.session_state.df.columns.tolist()
            y_manual = st.selectbox(
                T[lang_code]["axis_y"],
                options=y_options,
                index=0
            )
        with col_sel3:
            color_options = [T[lang_code]["none"]] + [col for col, meta in st.session_state.metadata.items() if meta["type"] == "Nominal"]
            color_manual = st.selectbox(
                T[lang_code]["color_seg"],
                options=color_options,
                index=0
            )
            
        type_x = st.session_state.metadata[x_manual]["type"]
        type_y = "Ninguno" if y_manual == T[lang_code]["none"] else st.session_state.metadata[y_manual]["type"]
        
        # Chart names translated
        chart_names = {
            "Histograma": "Histogram" if lang_code == "en" else "Histograma",
            "Box Plot": "Box Plot" if lang_code == "en" else "Box Plot",
            "Gráfico de Barras": "Bar Chart" if lang_code == "en" else "Gráfico de Barras",
            "Gráfico de Sectores (Pie)": "Pie Chart" if lang_code == "en" else "Gráfico de Sectores (Pie)",
            "Línea de Conteo Temporal": "Time Series Count" if lang_code == "en" else "Línea de Conteo Temporal",
            "Dispersión (Scatter Plot)": "Scatter Plot" if lang_code == "en" else "Dispersión (Scatter Plot)",
            "Líneas de Relación": "Line Plot" if lang_code == "en" else "Líneas de Relación",
            "Gráfico de Líneas": "Line Chart" if lang_code == "en" else "Gráfico de Líneas",
            "Barras Agrupadas (Medias)": "Grouped Bars (Means)" if lang_code == "en" else "Barras Agrupadas (Medias)",
            "Box Plot Agrupado": "Grouped Box Plot" if lang_code == "en" else "Box Plot Agrupado",
            "Mapa Térmico de Frecuencias": "Frequency Heatmap" if lang_code == "en" else "Mapa Térmico de Frecuencias"
        }
        
        compatible_charts = []
        default_chart = ""
        
        if type_y == "Ninguno":
            if type_x == "Quantitative":
                compatible_charts = [chart_names["Histograma"], chart_names["Box Plot"]]
                default_chart = chart_names["Histograma"]
            elif type_x == "Nominal":
                compatible_charts = [chart_names["Gráfico de Barras"], chart_names["Gráfico de Sectores (Pie)"]]
                default_chart = chart_names["Gráfico de Barras"]
            elif type_x == "Temporal":
                compatible_charts = [chart_names["Línea de Conteo Temporal"]]
                default_chart = chart_names["Línea de Conteo Temporal"]
        else:
            if type_x == "Quantitative" and type_y == "Quantitative":
                compatible_charts = [chart_names["Dispersión (Scatter Plot)"], chart_names["Líneas de Relación"]]
                default_chart = chart_names["Dispersión (Scatter Plot)"]
            elif type_x == "Temporal" and type_y == "Quantitative":
                compatible_charts = [chart_names["Gráfico de Líneas"]]
                default_chart = chart_names["Gráfico de Líneas"]
            elif type_x == "Nominal" and type_y == "Quantitative":
                compatible_charts = [chart_names["Barras Agrupadas (Medias)"], chart_names["Box Plot Agrupado"]]
                default_chart = chart_names["Barras Agrupadas (Medias)"]
            elif type_x == "Nominal" and type_y == "Nominal":
                compatible_charts = [chart_names["Mapa Térmico de Frecuencias"]]
                default_chart = chart_names["Mapa Térmico de Frecuencias"]
                
        if not compatible_charts:
            render_warning_card(T[lang_code]["compat_warning"])
        else:
            selected_chart = st.selectbox(T[lang_code]["suggested_chart_type"], options=compatible_charts, index=compatible_charts.index(default_chart))
            
            col_render, col_man_insight = st.columns([2, 1])
            
            with col_render:
                fig_man = None
                title_man = f"{selected_chart} de {x_manual}" + (f" vs {y_manual}" if y_manual != T[lang_code]["none"] else "")
                
                try:
                    c_color = None if color_manual == T[lang_code]["none"] else color_manual
                    
                    if selected_chart == chart_names["Histograma"]:
                        fig_man = px.histogram(st.session_state.df, x=x_manual, color=c_color)
                    elif selected_chart == chart_names["Box Plot"]:
                        fig_man = px.box(st.session_state.df, y=x_manual, color=c_color)
                    elif selected_chart == chart_names["Gráfico de Barras"]:
                        counts = st.session_state.df[x_manual].value_counts().reset_index()
                        counts.columns = [x_manual, "Frecuencia" if lang_code == "es" else "Frequency"]
                        fig_man = px.bar(counts, x=x_manual, y="Frecuencia" if lang_code == "es" else "Frequency")
                    elif selected_chart == chart_names["Gráfico de Sectores (Pie)"]:
                        counts = st.session_state.df[x_manual].value_counts().reset_index()
                        counts.columns = [x_manual, "Proporción" if lang_code == "es" else "Proportion"]
                        fig_man = px.pie(counts, names=x_manual, values="Proporción" if lang_code == "es" else "Proportion")
                    elif selected_chart == chart_names["Línea de Conteo Temporal"]:
                        counts = st.session_state.df.groupby(x_manual).size().reset_index(name="Conteo" if lang_code == "es" else "Count")
                        fig_man = px.line(counts, x=x_manual, y="Conteo" if lang_code == "es" else "Count")
                    elif selected_chart == chart_names["Dispersión (Scatter Plot)"]:
                        fig_man = px.scatter(st.session_state.df, x=x_manual, y=y_manual, color=c_color, trendline="ols" if c_color is None else None)
                    elif selected_chart == chart_names["Líneas de Relación"]:
                        fig_man = px.line(st.session_state.df, x=x_manual, y=y_manual, color=c_color)
                    elif selected_chart == chart_names["Gráfico de Líneas"]:
                        fig_man = px.line(st.session_state.df, x=x_manual, y=y_manual, color=c_color)
                    elif selected_chart == chart_names["Barras Agrupadas (Medias)"]:
                        agg_man = st.session_state.df.groupby(x_manual)[y_manual].mean().reset_index()
                        fig_man = px.bar(agg_man, x=x_manual, y=y_manual, color=c_color if c_color else x_manual)
                    elif selected_chart == chart_names["Box Plot Agrupado"]:
                        fig_man = px.box(st.session_state.df, x=x_manual, y=y_manual, color=c_color if c_color else x_manual)
                    elif selected_chart == chart_names["Mapa Térmico de Frecuencias"]:
                        cross_tab = pd.crosstab(st.session_state.df[x_manual], st.session_state.df[y_manual])
                        fig_man = px.imshow(cross_tab, text_auto=True, aspect="auto")
                        
                    if fig_man is not None:
                        fig_man = styles.apply_premium_style(fig_man, title_man, selected_theme)
                        st.plotly_chart(fig_man, use_container_width=True, key="manual_chart")
                    else:
                        render_error_card(T[lang_code]["render_error"])
                except Exception as ex_man:
                    render_error_card(f"{T[lang_code]['render_error']}: {ex_man}")
                    if selected_chart == chart_names["Dispersión (Scatter Plot)"]:
                        try:
                            fig_man = px.scatter(st.session_state.df, x=x_manual, y=y_manual, color=c_color)
                            fig_man = styles.apply_premium_style(fig_man, title_man, selected_theme)
                            st.plotly_chart(fig_man, use_container_width=True, key="manual_chart_fallback")
                        except Exception as e_fb:
                            render_error_card(f"Fallback error: {e_fb}")
                            
            with col_man_insight:
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-title">{T[lang_code]["manual_stats_title"]}</div>
                """, unsafe_allow_html=True)
                
                x_meta = st.session_state.metadata[x_manual]
                st.markdown(f"**{T[lang_code]['var_x']} ({x_manual}):**")
                for ins in x_meta["insights"]:
                    st.markdown(f"- {ins}")
                    
                if y_manual != T[lang_code]["none"]:
                    y_meta = st.session_state.metadata[y_manual]
                    st.markdown(f"<br>**{T[lang_code]['var_y']} ({y_manual}):**", unsafe_allow_html=True)
                    for ins in y_meta["insights"]:
                        st.markdown(f"- {ins}")
                        
                    st.markdown(f"<br>**{T[lang_code]['bivariate_analysis']}:**", unsafe_allow_html=True)
                    found_bi = False
                    for bi_ins in st.session_state.bivariate_insights:
                        cols = bi_ins["cols"]
                        if (x_manual in cols and y_manual in cols):
                            st.markdown(bi_ins["text"])
                            found_bi = True
                            break
                    if not found_bi:
                        st.markdown(f"*{T[lang_code]['no_bivariate_detected']}*")
                        
                st.markdown("</div>", unsafe_allow_html=True)

    # ── TAB 3: DATA PREVIEW TABLE ─────────────────────────────────────────────────
    with tab_data:
        st.markdown(f"### {T[lang_code]['data_preview_title']}")
        st.caption(f"{T[lang_code]['data_preview_subtitle']} '{st.session_state.file_name}' ({len(st.session_state.df)} rows total).")
        st.dataframe(st.session_state.df.head(100), use_container_width=True)
        
        st.markdown(f"### {T[lang_code]['summary_table_title']}")
        summary_rows = []
        for col, meta in st.session_state.metadata.items():
            summary_rows.append({
                T[lang_code]["summary_col"]: col,
                T[lang_code]["summary_inferred"]: meta["type"],
                T[lang_code]["summary_orig"]: meta["original_type"],
                T[lang_code]["summary_unique"]: meta["n_distinct"],
                T[lang_code]["summary_null"]: f"{meta['n_missing']} ({meta['p_missing']*100:.1f}%)"
            })
        st.table(pd.DataFrame(summary_rows))

# Footer section (always displayed at the bottom of the app)
st.markdown("---")
footer_logo_src = ""
try:
    footer_logo_b64 = get_base64_image("acvc-logo.png")
    footer_logo_src = f"data:image/png;base64,{footer_logo_b64}"
except Exception:
    pass

if footer_logo_src:
    footer_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; padding: 10px 0; color: #718096; font-size: 0.9rem; font-family: 'Inter', sans-serif;">
        <img src="{footer_logo_src}" style="height: 28px; vertical-align: middle; border-radius: 4px;">
        <span>{T[lang_code]['developed_by']} <strong>ACVC</strong></span>
    </div>
    """
else:
    footer_html = f"""
    <div style="display: flex; align-items: center; justify-content: center; padding: 10px 0; color: #718096; font-size: 0.9rem; font-family: 'Inter', sans-serif;">
        <span>{T[lang_code]['developed_by']} <strong>ACVC</strong></span>
    </div>
    """
st.markdown(footer_html, unsafe_allow_html=True)
