# DEMATEL Toolkit

A desktop application for cause-and-effect analysis using DEMATEL and its extensions. Built with Python and PySide6, it provides an interactive GUI for entering expert judgments, running the analysis, visualizing results, and generating AI-powered interpretations.

---

## Features

- **Four solver types:** Classical DEMATEL, Fuzzy DEMATEL, Grey DEMATEL, and Fuzzy Z-DEMATEL
- **Multi-expert support** with customizable weights
- **Five threshold methods:** Average, First Quartile, Median, Third Quartile, and Maximum Mean De-Entropy (MMDE)
- **Interactive matrix editor** with linguistic dropdown inputs per expert
- **Results viewer** with tabs for matrices, R/C scores, causal diagram, and heatmap
- **Cluster analysis** of the total relation matrix (K-Means and Hierarchical)
- **Export** results to XLSX and visualizations to PNG
- **AI-generated explanation** of results via Gemini, OpenAI, OpenRouter, or Groq

---

## Requirements

- Python 3.10 or higher
- Windows, macOS, or Linux

---

## Installation

### From GitHub

```bash
pip install git+https://github.com/atorkayesh/DEMATEL_Toolkit.git
```

### From source

```bash
git clone https://github.com/atorkayesh/DEMATEL_Toolkit.git
cd DEMATEL_Toolkit
pip install .
```

---

## Usage

After installation, launch the application from the terminal:

```bash
DEMATEL-Toolkit
```

### Workflow

1. Select a **solver type** and **threshold method** from the Setup panel
2. Set the number of **experts** and **factors**
3. Click **Generate Input Forms** and fill in factor and expert names with weights
4. Click **Next: Create Matrix Editor** and fill in the linguistic judgment matrix for each expert
5. Click **Run Analysis** to compute results
6. Browse the **Results** tabs: Summary, Matrices, R/C Scores, Causal Diagram, Heatmap
7. Optionally generate an **AI Explanation** by selecting an engine and entering your API key

---

## Supported Linguistic Scales

**Standard / Fuzzy / Grey DEMATEL**
| Label | Crisp | Fuzzy (l, m, u) | Grey [l, u] |
|---|---|---|---|
| No influence | 0 | (0.00, 0.00, 0.25) | [0.00, 0.00] |
| Low influence | 1 | (0.00, 0.25, 0.50) | [0.00, 0.25] |
| Medium influence | 2 | (0.25, 0.50, 0.75) | [0.25, 0.50] |
| High influence | 3 | (0.50, 0.75, 1.00) | [0.50, 0.75] |
| Extreme influence | 4 | (0.75, 1.00, 1.00) | [0.75, 1.00] |

**Fuzzy Z-DEMATEL** uses combined influence–reliability judgments (e.g. *"High influence with M reliability"*), where reliability levels are VL, L, M, H, and VH.

---

## AI Explanation

The AI tab generates an academic-style narrative interpretation of the results. Supported engines:

| Engine | Example models |
|---|---|
| Gemini | gemini-2.5-pro, gemini-2.0-flash |
| OpenAI | gpt-4o, gpt-4o-mini |
| OpenRouter | openai/gpt-4o-mini, mistralai/mistral-7b-instruct |
| Groq | llama-3.3-70b-versatile, mixtral-8x7b-32768 |

An API key is required. Keys are never stored — they are only held in memory for the duration of the session.

---

## Project Structure

```
DEMATEL_Toolkit/
├── dematel_tool/
│   ├── __init__.py
│   ├── __main__.py
│   ├── gui_app.py                  # Main window
│   ├── matrix_editor_widget.py     # Expert matrix input
│   ├── results_viewer_widget.py    # Results tabs and export
│   ├── analysis_service.py         # Solver dispatcher
│   ├── dematel_core.py             # Classical DEMATEL engine
│   ├── fuzzy_dematel_core.py       # Fuzzy DEMATEL engine
│   ├── grey_dematel_core.py        # Grey DEMATEL engine
│   ├── fuzzy_z_dematel_core.py     # Fuzzy Z-DEMATEL conversion
│   ├── clustering_service.py       # K-Means / Hierarchical clustering
│   ├── mmde_service.py             # MMDE threshold algorithm
│   ├── export_service.py           # XLSX and PNG export
│   ├── llm_explanation_service.py  # LLM API calls
│   ├── llm_worker.py               # Background QThread worker
│   ├── matrix_parsers.py           # Text / Excel matrix parsing
│   └── constants.py                # Scales, maps, enums
└── pyproject.toml
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
