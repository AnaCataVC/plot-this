# Deprecation of `pkg_resources` in Modern Python Environments

## Problem Context
When attempting to deploy the application on Streamlit Community Cloud using Python 3.11+, the environment failed to import the third-party library `fg-data-profiling` with the following error:
`ModuleNotFoundError: No module named 'pkg_resources'`

## Technical Analysis (Root Cause)
- `pkg_resources` was a legacy module bundled with `setuptools`.
- As of **setuptools version 82.0.0**, Python maintainers completely removed `pkg_resources` in favor of the new standard library `importlib.metadata` for performance and modernization reasons.
- Streamlit Cloud always installs the absolute latest version of `setuptools` (above 82) when building fresh environments ("clean installs").
- Abandoned or slowly maintained projects (like `ydata-profiling` or its fork `fg-data-profiling`) still have hard dependencies on `pkg_resources` embedded in their source code, which causes an instant crash upon import.

## Applied Resolution (Short-term Workaround)
To make the project compile and run without rewriting third-party library code, it is mandatory to pin the `setuptools` version in `requirements.txt` to a version prior to the "great purge":
```text
setuptools<81
```

## Long-term Recommendation
Monitor the releases of `fg-data-profiling`. Once the developers internally migrate their calls to `importlib.metadata`, the restriction in `requirements.txt` should be removed.
