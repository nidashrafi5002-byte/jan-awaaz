# 🏛️ Jan Awaaz (जन आवाज)

> **Multilingual AI-Powered Governance Platform for Digital Public Infrastructure (DPI)**

[![Deploy to Render](https://render.com/images/deploy-to-render.svg)](https://jan-awaaz.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg)](https://fastapi.tiangolo.com/)
[![Gemini API](https://img.shields.io/badge/Google%20Gemini-Powered-4285F4.svg)](https://ai.google.dev/)

---

## 📌 Overview

**Jan Awaaz** (Voice of the People) is an open-source, multilingual AI framework designed to bridge the gap between citizens and local governance bodies. Built for **Track 1: AI for Digital Public Infrastructure & Governance**, Jan Awaaz processes unstructured citizen grievances across **6 regional Indian languages** (Hindi, Bengali, Tamil, Telugu, Marathi, and Kannada) and transforms them into real-time, actionable insights for decision-makers.

By combining Google Gemini API with a resilient backend architecture, Jan Awaaz enables automated transcription, translation, categorisation, priority scoring, and spatial sentiment mapping on a unified administrative dashboard.

---

## ✨ Key Features

### 🎙️ 1. Multilingual Citizen Interface
* **Voice & Text Input:** Accepts natural speech or typed complaints in 6 major Indian languages.
* **Dialect & Slang Processing:** Leverages Google Gemini's multimodal understanding to extract intent from informal regional speech without requiring rigid official terminology.

### ⚡ 2. High-Availability AI Processing Pipeline
* **Structured Output Parsing:** Automatically classifies complaints into municipal categories (Water, Roads, Sanitation, Electricity) and assigns severity-based priority scores.
* **Automated Fallback Chain:** Implements an exponential fallback across Gemini model tiers (`gemini-3.1-flash-lite` → `gemini-3.8-flash` → `gemini-3.5-flash`) to guarantee **99.9% processing uptime** during high-concurrency traffic.

### 🗺️ 3. Policymaker Analytics Dashboard
* **Interactive Heatmaps:** Utilises **Leaflet.js** to map grievance density across districts, helping administrators spot hot-spots in real time.
* **Sentiment & SLA Analytics:** Powered by **Chart.js** to track resolution timelines, department responsiveness, and public sentiment shifts.

---

## 🏗️ Architecture Stack

```text
               ┌────────────────────────────────────────┐
               │    React + Tailwind Frontend UI        │
               │  (Citizen Portal & Admin Dashboard)    │
               └───────────────────┬────────────────────┘
                                   │ HTTPS / REST
                                   ▼
               ┌────────────────────────────────────────┐
               │         FastAPI Backend Engine         │
               └─────────┬────────────────────┬─────────┘
                         │                    │
        SQLAlchemy /     │                    │  Google Gemini API
        SQLite           ▼                    ▼  (Multimodal Translation
               ┌──────────────────┐  ┌─────────────────────────┐
               │ Local Database   │  │ Model Fallback Pipeline │
               │ (Grievance Store)│  │ 3.1-lite -> 3.8 -> 3.5  │
               └──────────────────┘  └─────────────────────────┘


