# Arquitectura Híbrida: Streamlit Cloud + Vercel

**Fecha:** 2026-06-25

## Contexto
Durante el despliegue del proyecto, optamos por una arquitectura híbrida donde Streamlit Community Cloud sirve como el motor de backend (y renderizado de UI pesado), mientras que Vercel aloja un sitio web estático ultra-rápido que embebe la aplicación mediante un `iframe`. Esto nos permitió usar un dominio personalizado y aislar el frontend estático.

A lo largo del proceso, nos topamos con tres bloqueos críticos de infraestructura que documentamos aquí para futuros despliegues.

## Lecciones Aprendidas (Gotchas y Soluciones)

### 1. Bucle de Redirecciones de Streamlit en Iframes
**Problema:** Al incrustar la URL directa (`https://app.streamlit.app/`) dentro de un iframe en Vercel, el navegador entraba en un bucle de redirecciones infinitas (a menudo arrojando códigos `403` o "Redirigido demasiadas veces").
**Por qué ocurre:** Streamlit activa mecanismos anti-clickjacking por defecto.
**Solución:** Es obligatorio anexar el parámetro de consulta `?embedded=true` a la URL del iframe.
```html
<!-- Correcto -->
<iframe src="https://tu-app.streamlit.app/?embedded=true"></iframe>
```

### 2. Configuración Estática en Vercel (`vercel.json`)
**Problema:** Vercel detecta automáticamente archivos `.py` y asume que el proyecto usa "Serverless Functions" de Python, rompiendo el despliegue al buscar una variable `app` exportada. Al intentar forzar el comportamiento estático declarando `"src": "index.html"`, Vercel ignora el resto de assets (como favicons `.png` o CSS), resultando en errores 404.
**Solución:** Se debe usar un arreglo expansivo (wildcards) en el archivo de configuración para incluir todos los assets estáticos.
```json
{
  "version": 2,
  "builds": [
    {
      "src": "*.{html,png,ico,svg,css,js}",
      "use": "@vercel/static"
    }
  ]
}
```

### 3. Crash por Dependencias Obsoletas (`pkg_resources`)
**Problema:** Librerías de datos legacy o no actualizadas recientemente (como `fg-data-profiling` o antiguos forks de `ydata-profiling`) fallan crasheadas en la nube con `ModuleNotFoundError: No module named 'pkg_resources'`.
**Por qué ocurre:** Las versiones de `setuptools >= 82.0.0` (lanzadas en 2026) eliminaron por completo el módulo `pkg_resources`.
**Solución:** Se debe fijar la versión de `setuptools` explícitamente en el `requirements.txt` a una versión anterior a la purga, hasta que la librería tercera actualice su código a `importlib.metadata`.
```text
# requirements.txt
setuptools<81
```
