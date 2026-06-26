# Project Specific Rules (plot-this)

## Context
`plot-this` is a local Streamlit + Plotly interactive data visualization tool that must run blazing fast without internet dependencies, handling heavy statistical analysis exclusively in memory.

## 🚫 Data Library Constraints in Streamlit
- **Avoid Heavy Profilers:** NEVER use libraries like `ydata-profiling`, `pandas-profiling`, or `fg-data-profiling` within this Streamlit ecosystem. Their internal multiprocessing dependencies (`multiprocessing`) and console progress bars (`tqdm`) cause severe deadlocks, memory leaks, and network-blocking issues on Windows environments.
- **Use Pure Pandas:** To extract metadata, bivariate correlations, skewness, or null value counts, you must build the logic manually using **ONLY native pure Pandas functions** (e.g., `df.corr()`, `df.value_counts()`, `df.skew()`, `df.isna().sum()`). This guarantees millisecond execution times and completely eliminates serialization problems within the Streamlit cache.

## 🎨 Streamlit UI & UX Best Practices
- **UI Reactivity and `st.rerun()`**: If a widget (such as a `file_uploader` or button) is placed inside a conditional layout block (e.g., `if state is None:`) and its interaction updates the state to render a completely different layout branch, you MUST call `st.rerun()` immediately after updating `st.session_state`. Otherwise, Streamlit will finish rendering the current block top-to-bottom, and the user will feel like "nothing happened" until a second interaction forces a redraw.
- **Agnostic UI Text**: Use broad action verbs like "Upload" instead of specific interactions like "Drag and drop", since components often allow multiple interaction modes. When moving layout components (e.g., from a sidebar to the main space), ALWAYS search and update any instructional text or translations (e.g., in `locales.py`) that might contain outdated spatial references (like "left panel").
- **Error Handling UX**: NEVER print raw, full Python tracebacks in the main UI for the end user to see. Always display a friendly, actionable error message, and hide the technical traceback log inside a collapsible component like `st.expander("View technical details")` to avoid intimidating non-technical users.
