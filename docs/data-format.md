# Formato de Datos Soportado en PlotThis

Para asegurar que el motor de inferencia semántica y el generador de gráficos funcionen con la máxima precisión, te recomendamos preparar tus archivos CSV o Excel siguiendo las siguientes directrices:

---

## 1. Cabeceras en la Primera Fila
*   La primera fila de tu archivo debe contener los nombres descriptivos de cada columna (ej. `Fecha`, `Producto`, `Ventas`, `Presupuesto_Marketing`).
*   Evita dejar la primera fila vacía o usar nombres duplicados, ya que esto podría causar errores en el parseo inicial de Pandas.

## 2. Formato de Fechas (Variables Temporales)
El motor de tipado busca y analiza patrones comunes de fecha. Para asegurar una correcta inferencia como variable **`Temporal`**, utiliza formatos estándar como:
*   `YYYY-MM-DD` (ej. `2026-01-25`)
*   `YYYY-MM-DD HH:MM:SS` (ej. `2026-01-25 14:30:00`)
*   `DD/MM/YYYY` (ej. `25/01/2026`)

*Nota:* Si una columna contiene fechas con formatos mixtos o inconsistentes, podría ser catalogada como variable Categórica (Nominal).

## 3. Limpieza de Números (Variables Cuantitativas)
Las columnas numéricas deben contener exclusivamente dígitos y puntos decimales para ser clasificadas como **`Quantitative`**:
*   **Símbolos de Moneda:** Evita incluir símbolos de moneda (como `$`, `€`) o letras dentro de las celdas en tu archivo de datos crudo (ej: usa `4500` en lugar de `$4,500` o `4500 USD`).
*   **Separadores de Millares:** Se recomienda no usar separadores de millares con comas si no es estrictamente necesario, ya que puede confundir al parser (ej. usa `15000` en lugar de `15,000`). El separador decimal debe ser el punto `.`.
*   *Coerción de Cardinalidad:* Si una columna numérica contiene pocos valores únicos (menos de 10 categorías discretas, como códigos `[0, 1, 2]`), el motor la tratará como **`Nominal`** para facilitar gráficos de barras agrupados y comparativas lógicas.

## 4. Variables Categóricas (Nominal)
*   Representan texto, categorías o etiquetas (ej. `Tecnologia`, `Hogar`, `Ropa`).
*   Si una columna categórica posee una **alta cardinalidad** (más de 15 categorías únicas), la herramienta te lo advertirá en los insights univariantes y sugerirá gráficos horizontales ordenados con barras de desplazamiento para evitar que las etiquetas se solapen en pantalla.

## 5. Valores Faltantes (Nulos)
*   No es necesario que elimines las filas con valores faltantes. La herramienta gestiona automáticamente los vacíos (`NaN`, `None`, celdas en blanco) omitiéndolos en los cálculos matemáticos para que no distorsionen los promedios ni correlaciones.
*   En la tarjeta de insights univariantes se reportará de forma explícita el recuento y porcentaje de valores nulos encontrados por columna.
