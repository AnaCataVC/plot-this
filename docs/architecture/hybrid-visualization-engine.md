> **Created:** 2026-06-24
> **Last Updated:** 2026-06-26

# Learnings and Architecture: Hybrid Visualization Engine (Non-AI)

This document records the architectural decisions, lessons learned, and technical solutions applied during the development of the chart generation and recommendation tool.

---

## 1. Architectural Decisions

### A. Pure Pandas Data Profiling Engine
*   **Decision:** We entirely abandoned heavy third-party profilers like `ydata-profiling` and `fg-data-profiling` in favor of a custom, lightweight semantic inference engine built entirely on native Pandas methods (`df.corr()`, `df.skew()`, `df.value_counts()`).
*   **Why:** Streamlit's architecture on Windows is notoriously sensitive to heavy multiprocessing dependencies (`multiprocessing`) and console progress bars (`tqdm`) bundled inside these profilers, which caused severe deadlocks, memory leaks, and network-blocking issues.
*   **Implementation:** The entire inference logic runs in memory using vectorized Pandas operations (see `analyzer.py`). This guarantees millisecond execution times and completely eliminates serialization problems within the Streamlit cache. For massive datasets, we sample down to `MAX_ROWS = 10000` to maintain blazing fast performance.

### B. Streamlit + Plotly Express as UI Layer and Premium Design
*   **Decision:** We selected a monolithic local Python architecture over an SPA (React/Vite) + Backend (FastAPI) development.
*   **Why:** Python is the gold standard in statistical processing. Plotly Express allows exceptional interactivity (zoom, hover, vector export) that can be dressed in a premium way directly from Python code without requiring state synchronization or complex APIs.

---

## 2. Technical Gotchas and Lessons Learned

### A. Low-Cardinality Discrete Numeric Variables
*   **Problem:** Numeric columns representing discrete categories (like codes `[0, 1, 2]`) were classified as continuous quantitative, suggesting irrelevant histograms.
*   **Solution:** We implemented a coercion rule in `analyzer.py` that reclassifies numeric columns with a cardinality of fewer than 10 unique values as `Nominal` (Categorical) type, forcing more readable suggestions like bar charts or mean comparisons.

### B. Running Streamlit on Windows
*   **Problem:** When installing dependencies on Windows, Streamlit binaries and executables are saved in the local Python scripts folder, which is rarely registered in the system's `PATH` environment variable, causing failures when running the global `streamlit` command.
*   **Solution:** Run the application alternatively using the Python module execution command: `python -m streamlit run app.py`.

---

## 3. Coexisting Hybrid Deployment Pattern

One of the main project learnings was to structure a **single GitHub repository capable of feeding two different free cloud platforms without interfering with each other**:

1.  **Vercel (Static):** Reads and deploys the [index.html](file:///c:/Users/anaca/Repos/plot-this/index.html) file from the root for free, serving a full-screen iframe that masks the **Namecheap** custom domain.
2.  **Streamlit Community Cloud (Python Server):** Ignores the static HTML file and directly executes [app.py](file:///c:/Users/anaca/Repos/plot-this/app.py) to boot up the data processing and interactive charts backend.

This design pattern allows the user to have a product experience with a professional brand domain, free of server charges, and without the overhead of maintaining multiple repositories.
