# Hybrid Architecture: Streamlit Cloud + Vercel

**Date:** 2026-06-25

## Context
During the project's deployment, we opted for a hybrid architecture where Streamlit Community Cloud serves as the backend engine (and heavy UI renderer), while Vercel hosts an ultra-fast static website that embeds the application via an `iframe`. This allowed us to use a custom domain and isolate the static frontend.

Throughout the process, we encountered several critical infrastructure blockers which we document here for future deployments.

## Lessons Learned (Gotchas & Solutions)

### 1. Streamlit Redirect Loop in Iframes
**Problem:** When embedding the direct URL (`https://app.streamlit.app/`) inside an iframe in Vercel, the browser entered an infinite redirect loop (often throwing `403` codes or "Redirected you too many times" errors).
**Why it happens:** Streamlit activates anti-clickjacking security mechanisms by default.
**Solution:** It is mandatory to append the `?embedded=true` query parameter to the iframe URL.
```html
<!-- Correct -->
<iframe src="https://your-app.streamlit.app/?embedded=true"></iframe>
```

### 2. Vercel Static Configuration (`vercel.json`)
**Problem:** Vercel automatically detects `.py` files and assumes the project uses Python "Serverless Functions", breaking the deployment by searching for an exported `app` variable. When attempting to force static behavior by declaring `"src": "index.html"`, Vercel ignores the rest of the assets (like `.png` favicons or CSS), resulting in 404 errors.
**Solution:** An expansive array (wildcards) must be used in the configuration file to include all static assets.
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

### 3. Crash due to Obsolete Dependencies (`pkg_resources`)
**Problem:** Legacy data libraries or those not recently updated (such as `fg-data-profiling` or old forks of `ydata-profiling`) crash in the cloud with `ModuleNotFoundError: No module named 'pkg_resources'`.
**Why it happens:** Versions of `setuptools >= 82.0.0` (released in 2026) completely removed the `pkg_resources` module.
**Solution:** The `setuptools` version must be explicitly pinned in `requirements.txt` to a version prior to the purge, until the third-party library updates its code to `importlib.metadata`.
```text
# requirements.txt
setuptools<81
```

### 4. Silent Rejection of Heavy Favicons
**Problem:** Even though Vercel properly serves the file (returning HTTP 200), modern browsers ignore the tab icon and display a globe if the PNG image is too large (e.g., an original logo $>1$ MB).
**Why it happens:** Browsers prioritize main rendering performance and abort the decoding of massive icons to prevent blocking the UI thread.
**Solution:** Always resize logos to lightweight standard formats (`32x32` or `64x64`) and preferably use the `.ico` format. It is crucial to ensure that the `.ico` extension is included in the `vercel.json` (as shown in point 2) and update the HTML:
```html
<link rel="icon" href="favicon.ico" type="image/x-icon">
```
