# WhatsApp Chat Intelligence

An advanced conversational analytics and NLP intelligence dashboard for exported WhatsApp conversations. Built with Python, Streamlit, Pandas, Plotly, and NLTK to deliver deep behavioral insights, temporal patterns, interactive 2D/3D visualizations, and sentiment analysis.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Supported Export Formats](#supported-export-formats)
- [Prerequisites](#prerequisites)
- [Installation & Quick Start](#installation--quick-start)
  - [1. Clone or Open Project Directory](#1-clone-or-open-project-directory)
  - [2. Virtual Environment Setup](#2-virtual-environment-setup)
  - [3. Install Required Dependencies](#3-install-required-dependencies)
  - [4. Launch the Dashboard](#4-launch-the-dashboard)
- [Exporting WhatsApp Chats](#exporting-whatsapp-chats)
  - [Android Devices](#android-devices)
  - [iOS Devices (iPhone)](#ios-devices-iphone)
- [Dashboard Analytics Breakdown](#dashboard-analytics-breakdown)
  - [1. High-Level KPI Stat Cards](#1-high-level-kpi-stat-cards)
  - [2. Temporal Trends & Cumulative Trajectory](#2-temporal-trends--cumulative-trajectory)
  - [3. 3D Volume Topology & Circadian Rhythms](#3-3d-volume-topology--circadian-rhythms)
  - [4. Participant Persona Matrix](#4-participant-persona-matrix)
  - [5. Vocabulary & Stopword-Filtered Word Cloud](#5-vocabulary--stopword-filtered-word-cloud)
  - [6. Emoji Analytics](#6-emoji-analytics)
  - [7. VADER Sentiment Polarity Engine](#7-vader-sentiment-polarity-engine)
  - [8. Real-Time Message Search & CSV Export](#8-real-time-message-search--csv-export)
- [Privacy & Data Security](#privacy--data-security)
- [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## Overview

WhatsApp conversations represent rich historical records of group dynamics, collaboration patterns, and interpersonal sentiment. Standard chat logs, however, are unstructured plain text files that are cumbersome to analyze.

**WhatsApp Chat Intelligence** transforms raw chat logs into a fully interactive analytical suite. It handles varied international timestamp formats across Android and iOS platforms, extracts linguistic features, calculates behavioral metrics, and renders publication-ready 2D and 3D visual models.

---

## System Architecture

```
whatsapp-chat-analyser/
├── app.py                      # Streamlit application layout, theming, controls & state
├── preprocess.py               # Multi-format timestamp regex parser & feature extractor
├── helper.py                   # Statistical aggregation, Plotly chart builders & NLP engine
├── stop_hinglish.txt           # Multilingual stop word dictionary (English & Hinglish)
├── requirements.txt            # Explicit dependency specifications
├── .gitignore                  # Git exclude rules for virtual env and caches
└── MSEC AI&DS-4th-YEAR-...txt  # Built-in sample chat dataset for immediate testing
```

### Data Pipeline Flow

```
[Raw WhatsApp .txt Export]
           │
           ▼
[preprocess.py]
  • Multi-format timestamp pattern detection (Android / iOS / 12h / 24h)
  • Non-breaking space normalization (\u202f, \xa0)
  • Message vs System notification separation
  • Chronological sorting & temporal feature extraction (year, month, day, hour, period)
           │
           ▼
[helper.py]
  • Numerical KPI aggregations (messages, words, media, links, active days)
  • Circadian matrix compilation (7 days × 24 hours)
  • NLTK VADER sentiment scoring & polarity classification
  • URL stripping, stop word filtering & Word Cloud generation
  • Plotly 2D & 3D figure generation
           │
           ▼
[app.py (Streamlit Dashboard)]
  • Reactive theme engine (Dark Mode / Light Mode with dynamic CSS)
  • Tabbed modular layout with CSS hover animations
  • Interactive chart inspection, keyword filtering & CSV export
```

---

## Key Features

- **Universal Multi-Platform Parser**: Robust regex pipeline supporting Android (12-hour AM/PM and 24-hour clocks), iOS square-bracket exports (`[DD/MM/YY, hh:mm:ss]`), 2-digit/4-digit years, and unicode non-breaking space characters.
- **Dual Display Modes**: Instant toggle between Dark Mode and Light Mode with responsive CSS variables and coordinated Plotly visual palettes.
- **Interactive 3D Volume Topology**: A 360-degree rotatable 3D surface plot mapping Day of Week vs. Hour of Day vs. Message Density with floor contour projections.
- **24-Hour Circadian Polar Clock**: Circular radar chart illustrating diurnal conversational rhythms across day and night.
- **Participant Persona Matrix**: Multi-dimensional bubble scatter plot mapping total volume against verbosity (average words per message) and media volume.
- **VADER Sentiment Analysis**: Polarity breakdown (Positive, Neutral, Negative), sentiment ratio calculations, and monthly emotional polarity trends.
- **Zero Interface Clutter**: Completely clean, professional typography and layout without AI-typical decorative emojis in titles, headers, and navigation tabs.
- **Instant Testing**: One-click "Load Sample Conversation" button allows immediate exploration of all features without requiring your own chat export.

---

## Supported Export Formats

| Operating System | Time Format | Example Pattern | Support Status |
| :--- | :--- | :--- | :--- |
| **Android** | 24-Hour Clock | `12/31/22, 23:59 - Name: Message` | Supported |
| **Android** | 12-Hour Clock (AM/PM) | `12/31/22, 11:59 pm - Name: Message` | Supported |
| **Android** | 4-Digit Year | `31/12/2022, 10:15 - Name: Message` | Supported |
| **iOS / iPhone** | Square Bracket (24h) | `[31/12/22, 23:59:00] Name: Message` | Supported |
| **iOS / iPhone** | Square Bracket (12h) | `[12/31/22, 11:59:00 PM] Name: Message` | Supported |
| **International** | Hyphen / Dot Date | `2022-12-31, 23:59 - Name: Message` | Supported |

---

## Prerequisites

- **Python Version**: Python `3.10` or `3.11` (Python 3.11 recommended).
- **Operating System**: Windows, macOS, or Linux.
- **RAM**: 2 GB minimum (4 GB recommended for chats with over 50,000 messages).

---

## Installation & Quick Start

### 1. Clone or Open Project Directory

Open your command prompt or terminal in the project directory:

```bash
cd "c:\Users\DELL\Documents\My projects\whatsapp chat analyser"
```

### 2. Virtual Environment Setup

A virtual environment isolates dependencies and prevents version conflicts.

#### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note for PowerShell Execution Policy**: If you receive a script execution restriction error, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

#### Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

#### macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Dependencies

Install all pinned packages from `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Launch the Dashboard

Run the Streamlit application:

```bash
streamlit run app.py
```

Or run directly through the virtual environment path without activating:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

The application will launch automatically in your default browser at:
`http://localhost:8501`

---

## Exporting WhatsApp Chats

To analyze your own conversations, export the chat directly from WhatsApp as a text file.

### Android Devices
1. Open the target WhatsApp individual or group conversation.
2. Tap the **three dots menu** (top-right corner).
3. Select **More** -> **Export chat**.
4. When prompted, select **Without Media** *(attaching media generates large archives; the text log contains all message timestamps and media markers)*.
5. Save or transfer the generated `.txt` file to your computer.

### iOS Devices (iPhone)
1. Open the target WhatsApp conversation.
2. Tap the contact or group name at the top of the chat window to open **Contact Info** / **Group Info**.
3. Scroll to the bottom and tap **Export Chat**.
4. Select **Without Media**.
5. Save the `.txt` file via AirDrop, iCloud Drive, Email, or Files app to your computer.

---

## Dashboard Analytics Breakdown

### 1. High-Level KPI Stat Cards
Located directly at the top of the dashboard with fluid CSS hover elevations:
- **Total Messages**: Net message volume (excluding WhatsApp system alerts).
- **Total Words**: Word count computed across content messages.
- **Media Items**: Total count of images, videos, audio notes, stickers, and documents sent.
- **Shared Links**: Web URLs extracted using `urlextract`.
- **Active Days**: Total distinct calendar days on which messages were exchanged.
- **Avg Words / Msg**: Average linguistic density per message.

### 2. Temporal Trends & Cumulative Trajectory
- **Monthly Message Timeline**: Area-shaded line chart illustrating message volume across months.
- **Daily Activity Timeline**: Interactive daily timeline identifying volume spikes and milestones.
- **Cumulative Message Growth**: Trajectory curve showing overall conversation growth over time.

### 3. 3D Volume Topology & Circadian Rhythms
- **3D Conversational Volume Topology**: Interactive 3D surface plot mapping Day of Week vs. Hour of Day vs. Message Density. Click and drag to rotate 360 degrees, scroll to zoom, or hover to view exact message counts at any hourly coordinate.
- **Circadian 24-Hour Polar Clock**: Clock-style radar chart tracking conversational intensity throughout morning, afternoon, evening, and late-night cycles.
- **Weekly Hourly Heatmap**: 7x24 matrix highlighting the highest probability engagement windows.

### 4. Participant Persona Matrix
- **Behavioral Scatter Matrix**: Plots participant message count (X) against average words per message (Y), with bubble size reflecting media files sent and color displaying active days.
- **Contribution Percentage**: Quantitative breakdown of each member's percentage share of the group dialogue.

### 5. Vocabulary & Stopword-Filtered Word Cloud
- **Word Cloud**: High-resolution keyword cloud excluding URLs, punctuation, common English stop words, and conversational Hinglish particles.
- **High-Frequency Words**: Horizontal ranking chart of top keywords.

### 6. Emoji Analytics
- **Frequency Distribution**: Ranking of top emojis utilized in the conversation.
- **Full Emoji Registry**: Searchable tabular breakdown of every emoji encountered.

### 7. VADER Sentiment Polarity Engine
- **Sentiment Distribution**: Donut chart displaying the ratio of Positive, Neutral, and Negative messages.
- **Sentiment Ratio**: Clear quantitative comparison of constructive vs. critical language.
- **Monthly Sentiment Trendline**: Trajectory plot illustrating emotional shifts over the chat lifetime.

### 8. Real-Time Message Search & CSV Export
- **Keyword Search**: Filter the entire conversation in real time by specific words or phrases.
- **Date Range Slicing**: Narrow the analysis window to specific weeks, months, or years using the sidebar calendar selector.
- **CSV Export**: Download filtered messages with timestamp, user, and text columns as a CSV file with one click.

---

## Privacy & Data Security

- **100% Client-Side Processing**: All parsing, filtering, and metric computations run entirely in your local Python environment.
- **No Cloud Uploads**: Your chat messages and contact names are never transmitted to external APIs or third-party servers.
- **Local Lexicons**: Sentiment analysis is performed locally via the VADER lexicon on your machine.

---

## Troubleshooting & FAQs

### Q1: The app displays "Could not parse conversation timestamps"
- Ensure that the uploaded file is a plain `.txt` file exported directly from WhatsApp.
- Check that the first line contains a valid timestamp (e.g., `DD/MM/YY, HH:MM - ` or `[DD/MM/YY, HH:MM:SS]`).
- If using an edited file, ensure the timestamp format matches one of the supported patterns in the table above.

### Q2: PowerShell says `running scripts is disabled on this system`
Execute this command in your PowerShell terminal before activating the virtual environment:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Q3: `Port 8501 is already in use`
If another Streamlit instance is running, specify an alternative port:
```bash
streamlit run app.py --server.port 8502
```

### Q4: NLTK VADER Lexicon error on offline machines
If you are running in an environment without internet access, run this once while connected to download the lexicon:
```python
import nltk
nltk.download('vader_lexicon')
```

---

## Technical Specifications

- **Frontend**: Streamlit 1.35+
- **Data Engine**: Pandas 2.0+ & NumPy
- **Visuals**: Plotly Express & Plotly Graph Objects 5.20+
- **NLP & Lexical Processing**: NLTK VADER, WordCloud 1.9+, URLExtract, Emoji 2.10+
