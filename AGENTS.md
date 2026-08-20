# AGENTS.md — AI Agent Guidelines & Architecture Manual

This document serves as the operational manual, architecture reference, and workflow guide for AI coding agents operating within the **plot-this** repository.

---

## 1. Project Overview & Architecture

**plot-this** is an interactive, local-first data visualization and statistical exploration tool built with **Python**, **Streamlit**, **Pandas**, and **Plotly**. It provides instant dataset profiling, chart recommendations, correlation matrices, and distribution analysis entirely in-memory without external cloud dependencies.

### Core Modules:
- **`app.py`**: Main Streamlit user interface, multi-page state routing, and layout controls.
- **`analyzer.py`**: High-performance in-memory statistical analyzer using pure Pandas (summary statistics, skewness, missing values, correlation matrix).
- **`recommender.py`**: Smart chart recommendation heuristics based on column data types and distribution attributes.
- **`locales.py`**: Bilingual translation dictionaries (English & Spanish).
- **`styles.py`**: Custom CSS injections for Streamlit components and pastel themes.
- **`tests/test_analysis.py`**: Pytest test suite covering statistical calculations and edge cases.

---

## 2. Directory Structure

```text
plot-this/
├── app.py                     # Main Streamlit application entrypoint
├── analyzer.py                # Statistical analysis and profiling engine
├── recommender.py             # Chart type heuristic recommendation engine
├── locales.py                 # Bilingual dictionaries (EN/ES)
├── styles.py                  # Theme tokens and custom Streamlit styling
├── run_tests.py               # Test runner helper script
├── requirements.txt           # Python dependencies (streamlit, pandas, plotly, scipy, pytest)
├── tests/                     # Pytest suite
│   ├── conftest.py            # Shared fixtures
│   └── test_analysis.py       # Statistical and recommender tests
├── sample_data/               # Sample CSV datasets for testing & demos
├── docs/                      # Architecture, user guides, and learnings
└── README.md                  # Bilingual project documentation (EN/ES)
```

---

## 3. Mandatory Agent Rules & Directives

### 🌐 Language & Communication
- **Source Code**: All Python code (functions, variables, docstrings, comments) MUST be in **English**.
- **User Chat**: Communicate with the user in **Spanish** unless requested otherwise.
- **Git Commits**: Use **Conventional Commits** in **English** (e.g., `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`).
- **README**: Maintain bilingual documentation (English and Spanish).

### 🔒 Security & Privacy
- **Absolute Paths**: NEVER leak absolute user paths (e.g., `C:\Users\...`) into code, documentation, or commit messages. Always use relative paths (`sample_data/sales_data.csv`).
- **In-Memory Guarantee**: User datasets must remain strictly in memory or temporary sessions; never write uploaded dataset contents to unencrypted public directories.

### 💻 PowerShell Environment
- **Command Chaining**: NEVER use `&&` or `||` in terminal commands. Use `;` or separate sequential commands.
- **GitHub CLI Context**: Switch to personal account `AnaCataVC` (`gh auth switch -u AnaCataVC --hostname github.com 2>$null`).

---

## 4. Development & Build Commands (PowerShell)

### Run Streamlit App
```powershell
# Launch local Streamlit development server
streamlit run app.py
```

### Run Tests
```powershell
# Run pytest test suite
pytest tests/

# Alternative custom test runner
python run_tests.py
```

---

## 5. Streamlit Performance & UI Constraints

1. **Avoid Heavy Profilers**: NEVER use libraries like `ydata-profiling` or `pandas-profiling` inside this Streamlit ecosystem. Their internal multiprocessing and console progress bars cause deadlocks and memory spikes on Windows.
2. **Use Pure Pandas**: All descriptive statistics, correlations, skewness, and null checks must use pure Pandas (`df.corr()`, `df.value_counts()`, `df.skew()`, `df.isna().sum()`) to ensure sub-millisecond execution and cache stability.
3. **UI Reactivity and `st.rerun()`**: If a widget interaction inside a conditional layout modifies `st.session_state` to render a new layout branch, call `st.rerun()` immediately to force an immediate redraw.
4. **Friendly Error UX**: Never dump raw Python tracebacks into the primary UI. Show friendly status banners (`st.error`, `st.warning`) and wrap technical stack traces inside collapsible `st.expander("Technical details")`.
