# WhatsApp Chat Intelligence

A modern, high-performance conversational analytics dashboard for WhatsApp chat exports built with **Streamlit**, **Pandas**, **Plotly**, and **NLTK**.

---

## Key Features

- **Universal Parser**: Supports Android (12-hour AM/PM and 24-hour formats), iOS (`[date, time]` bracket formats), and multi-line messages.
- **Theme Modes**: One-click toggle between **Dark Mode** and **Light Mode** with matching Plotly themes.
- **Micro-Animations & Clean UI**: Fluid CSS transitions, hover elevations on KPI cards, and modern layout.
- **Interactive Visualizations**: Powered by Plotly (zoom, pan, inspect data points on hover).
- **Core Analytics Modules**:
  - **KPI Metrics**: Total messages, words, media shared, links shared, active days, average words per message.
  - **Timelines & Cumulative Growth**: Interactive monthly volume, daily trends, and cumulative conversation growth curve.
  - **3D Conversational Volume Topology**: Interactive 360-degree rotatable 3D surface plot mapping Day of Week vs Hour of Day vs Message Volume with contour floor projection.
  - **Circadian 24-Hour Polar Clock**: Circular radar chart displaying daily conversational rhythms.
  - **Participant Persona Matrix**: Multi-dimensional bubble chart mapping total activity vs verbosity (average words/msg) vs media shared.
  - **Activity Heatmap**: Day-of-week distribution and 24x7 hourly heatmap matrix.
  - **Text Analysis**: Clean Word Cloud and high-frequency keyword rankings.
  - **Emoji Usage**: Emoji frequency counts and distribution charts.
  - **Sentiment Analysis & Trajectory**: VADER-powered sentiment breakdown (Positive, Neutral, Negative), donut distribution, and monthly sentiment polarity trendline.
  - **Message Explorer**: Keyword search, date-range slicing, and CSV export.

---

## Installation & Setup

### 1. Activate the Virtual Environment
Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):
```cmd
.venv\Scripts\activate.bat
```

### 2. Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Or directly via the virtual environment:
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

---

## How to Export WhatsApp Chats
1. Open any WhatsApp individual or group chat.
2. Tap the three dots menu (Android) or contact name (iOS) -> **More** -> **Export chat**.
3. Select **Without Media**.
4. Upload the generated `.txt` file into the app using the sidebar uploader or test with the built-in sample dataset.

