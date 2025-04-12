# ✈️ Flight Delays Analysis

This project explores and analyses flight delay and cancellation data in the United States. Using Python, Pandas, and Plotly, it uncovers trends in airline punctuality, common delay reasons, seasonal effects, and more. The goal is to deliver interactive visual insights and build a dashboard for decision-makers and the general public.

---

## 📦 Dataset

- Source: [US DOT - Bureau of Transportation Statistics](https://www.kaggle.com/datasets/usdot/flight-delays)
- Includes over 500,000 domestic flight records with:
  - Departure/arrival delays
  - Airlines and airports
  - Scheduled vs. actual timings
  - Cancellation reasons
  - Delay types (carrier, weather, security, NAS, late aircraft)

---

## 📊 Features

- Cleaned and preprocessed raw flight data
- Extracted time features (month, weekday, hour)
- Built visualisations to identify:
  - Delay rates by airline, weekday, and hour
  - Cancellation reasons distribution
  - Heatmaps of delay patterns
  - Interactive maps of airport-level delays

---

## 🚀 Dashboard (Built with Streamlit)

You can explore the live dashboard (if hosted) or run it locally:

```bash
streamlit run dashboard.py
