> **Created:** 2026-06-25
> **Last Updated:** 2026-06-25

# Investigación: Deprecación de `pkg_resources` y `setuptools`

## Contexto del Problema
Al intentar desplegar la aplicación en Streamlit Cloud utilizando la librería `fg-data-profiling` bajo un entorno de Python reciente, nos topamos con el error crítico:
`ModuleNotFoundError: No module named 'pkg_resources'`

A pesar de incluir explícitamente `setuptools` en `requirements.txt`, el error continuaba fallando.

## Hallazgos Técnicos

1. **Eliminación Definitiva en `setuptools` 82.0.0 (Feb 2026):** 
   El módulo `pkg_resources` había estado en estado obsoleto (deprecated) por mucho tiempo debido a problemas de rendimiento y diseño monolítico. A partir de la versión `82.0.0` lanzada a principios de 2026, la Python Packaging Authority (PyPA) procedió a **eliminarlo por completo** de la librería `setuptools`.

2. **Dependencia Fuerte de Librerías de Terceros:**
   Muchas librerías, incluyendo `ydata-profiling` y sus forks iniciales como `fg-data-profiling`, internamente mantienen código legacy que hace llamados de la forma `import pkg_resources` en sus módulos de inicialización para validar versiones, cargar recursos o verificar entry points.

3. **La Solución a Corto Plazo (Workaround Seguro):**
   Hasta que todo el ecosistema y subdependencias actualicen su código, la PyPA y la comunidad recomiendan fuertemente realizar un *pinning* explícito de la versión antigua de `setuptools` para proyectos en producción.
   ```text
   setuptools<81
   # o alternativamente setuptools<=80.10.2
   ```

4. **La Solución Definitiva (Largo Plazo):**
   A largo plazo, las librerías deben abandonar cualquier uso de `pkg_resources` y migrar hacia las APIs nativas y modulares incluidas en el *Standard Library* de Python moderno:
   * Reemplazo para lectura de versiones o metadata: `importlib.metadata`
   * Reemplazo para carga de recursos (imágenes, CSV internos): `importlib.resources`
   * Reemplazo para parsing de requerimientos: `packaging.requirements`

## Conclusión Aplicada a Nuestro Proyecto
La medida que tomamos (fijar `setuptools<81` en `requirements.txt`) **sí es considerada por la comunidad y documentación oficial como la mejor y más segura solución inmediata a nivel de consumidor de la librería**, ya que la responsabilidad de reescribir ese código fuente y publicarlo utilizando `importlib.metadata` recae puramente en los mantenedores de `fg-data-profiling`. No existe un *shim* de reemplazo transparente (drop-in) que emule `pkg_resources` desde afuera.
