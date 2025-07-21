# HealthKart Influencer Campaign Dashboard

A Streamlit dashboard to analyze and visualize the ROI and performance of influencer campaigns across multiple brands and platforms.

---

## Features

- **Upload Data:** Upload your own CSV files for influencers, posts, tracking data, and payouts.
- **Filtering:** Filter by brand/product, influencer type (category), and platform.
- **Performance Tracking:** View post and influencer performance metrics.
- **ROI & ROAS:** Calculate and visualize Return on Investment (ROI) and Return on Ad Spend (ROAS).
- **Insights:** See top influencers, best personas, and influencers with poor ROAS.
- **Payout Tracking:** Track payouts to influencers.
- **Export:** Download filtered tracking data as CSV.

---

## Setup Instructions

1. **Clone the repository or download the code.**

2. **Create and activate a Python virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install streamlit pandas
   ```

4. **Run the dashboard:**
   ```sh
   streamlit run app.py
   ```
   Open the local URL provided in your terminal (usually http://localhost:8501).

---

## Required CSV File Formats

You must upload all four files for the dashboard to work.  
**Column names must match exactly (case-sensitive, no extra spaces).**

### 1. Influencers CSV
| ID | name | category | gender | follower_count | platform |
|----|------|----------|--------|----------------|----------|
| 1  | Alice | Fitness | F | 10000 | Instagram |
| ... | ... | ... | ... | ... | ... |

### 2. Posts CSV
| influencer_id | platform | date | URL | caption | reach | likes | comments |
|---------------|----------|------|-----|---------|-------|-------|----------|
| 1 | Instagram | 2024-06-01 | url1 | Great product! | 5000 | 400 | 40 |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 3. Tracking Data CSV
| source | campaign | influencer_id | user_id | product | date | orders | revenue |
|--------|----------|--------------|---------|---------|------|--------|---------|
| Instagram | C1 | 1 | 1001 | MuscleBlaze | 2024-06-01 | 10 | 1000 |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 4. Payouts CSV
| influencer_id | basis | rate | orders | total_payout |
|---------------|-------|------|--------|--------------|
| 1 | post | 100 | 10 | 1000 |
| ... | ... | ... | ... | ... |

---

## Assumptions

- **All four CSVs must be uploaded for the dashboard to display analytics.**
- **Column names must match exactly** (case-sensitive, no extra spaces).
- **Ad spend per order is assumed to be 50** (can be changed in the code).
- **No default data is shown**; only uploaded data is used.
- **Data validation**: The app checks for required columns and stops with an error if any are missing.
- **All calculations and filters are based on the uploaded data.**

---

## Troubleshooting

- If you see an error about missing columns, check your CSV headers for typos, extra spaces, or encoding issues.
- Save your CSVs as UTF-8 (comma-delimited) for best compatibility.
- If you need sample data, use the provided example files or ask for new ones.

---

## License

Open source, for educational and demonstration purposes. 

---

## Step-by-Step: Export Insights Summary as PDF

### 1. Install Required Library

You’ll need a library to generate PDFs. The most Streamlit-friendly options are:
- `fpdf` (simple, pure Python)
- `reportlab` (more advanced)
- `pdfkit` (requires wkhtmltopdf installed)

**Let’s use `fpdf` for simplicity.**

Install it:
```sh
pip install fpdf
```

---

### 2. Add PDF Export Code to app.py

Add this code after your Insights section, before the download button:

```python
from fpdf import FPDF
import tempfile
import streamlit as st
import base64
import os

def generate_insights_pdf(top_influencers, persona_perf, poor_rois):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "HealthKart Influencer Campaign Insights Summary", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Top Influencers by Revenue", ln=True)
    pdf.set_font("Arial", size=10)
    for idx, value in top_influencers.items():
        pdf.cell(0, 8, f"Influencer ID: {idx} | Revenue: {value}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Best Personas (by Category Revenue)", ln=True)
    pdf.set_font("Arial", size=10)
    for idx, value in persona_perf.items():
        pdf.cell(0, 8, f"Category: {idx} | Avg Revenue: {value:.2f}", ln=True)
    pdf.ln(5)

    if poor_rois is not None:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Influencers with Poor ROAS", ln=True)
        pdf.set_font("Arial", size=10)
        for idx, value in poor_rois.items():
            pdf.cell(0, 8, f"Influencer ID: {idx} | ROAS: {value:.2f}", ln=True)
        pdf.ln(5)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    temp_file.close()
    return temp_file.name

show_pdf = False
if st.button("Show Insights Summary as PDF"):
    poor_rois_data = poor_rois if 'poor_rois' in locals() else None
    pdf_path = generate_insights_pdf(top_influencers, persona_perf, poor_rois_data)
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    os.remove(pdf_path)
   