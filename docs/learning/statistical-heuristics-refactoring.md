# Aprendizajes: Refactorización de Heurísticas Estadísticas y Usabilidad de Gráficos

Durante la evaluación de la lógica de inferencia semántica y recomendación de gráficos en `plot-this`, se identificaron varios problemas clave que conectan el rigor estadístico con la usabilidad/UX de los datos.

## 1. Integridad Estadística vs. UX Visual (El "Dynamite Plot")
*   **Problema:** Priorizar diagramas de barras que muestran solo medias agrupadas oculta completamente la varianza, rango y presencia de valores atípicos. Esto puede llevar al usuario a asumir conclusiones sesgadas o incorrectas si las distribuciones de los grupos se solapan.
*   **Solución/Decisión:** Los **Diagramas de Caja Segmentados (Boxplots)** deben tener prioridad sobre las agregaciones de barras. Si se renderizan barras con medias, deben incluirse obligatoriamente barras de error (desviación estándar) para no engañar visualmente al usuario.

## 2. Fragilidad Matemática en Diferencia de Medias
*   **Problema:** La fórmula clásica de diferencia porcentual relativa `(max_mean - min_mean) / min_mean * 100` falla críticamente si el valor mínimo es `0` o negativo (provoca divisiones por cero o genera porcentajes infinitos sin sentido real).
*   **Solución/Decisión:** Reemplazar la diferencia relativa por la métrica de **Tamaño del Efecto (variación de la d de Cohen)**, normalizando la diferencia mediante la desviación estándar global:
    $$\text{Tamaño del efecto} = \frac{|\mu_{\text{max}} - \mu_{\text{min}}|}{\sigma_{\text{global}}}$$
    Un valor $\ge 0.5$ representa un efecto medio/significativo apto para generar insights automáticos.

## 3. Preservación del Tipo de Dato Ordinal
*   **Problema:** Tratar columnas numéricas discretas con pocos valores (ej. escalas del 1 al 10) como nominales (categóricas) destruye el orden natural y confunde al usuario si la UI ordena los valores por frecuencia en lugar de su secuencia matemática.
*   **Solución/Decisión:** Crear una distinción explícita para tipos numéricos discretos (`Discrete Numeric` u `Ordinal`). Esto permite aplicar palettes secuenciales en lugar de categóricas arbitrarias y mantener el orden en el eje visual.

## 4. Mitigación del Punto Ciego de Anscombe
*   **Problema:** Depender exclusivamente de la correlación de Pearson y ajustes lineales simples (`polyfit` grado 1) asume linealidad perfecta y es hipersensible a outliers.
*   **Solución/Decisión:** Calcular también la correlación de Spearman para capturar relaciones monótonas no lineales y priorizar el gráfico según la señal más fuerte entre Pearson y Spearman.

## 5. Control de la Densidad Visual (Overplotting)
*   **Problema:** Los gráficos de dispersión tradicionales con miles de puntos ($N > 5000$) se convierten en nubes densas ilegibles y lentas en la interfaz del navegador.
*   **Solución/Decisión:** Para grandes volúmenes de datos ($N > 5000$), degradar la prioridad del Scatter Plot clásico y priorizar Histogramas 2D o mapas de calor de densidad (Hexbins).
