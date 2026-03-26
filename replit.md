# Ronald Saenz – Gravimetría

## Project Overview
A geotechnical engineering web application for calculating and visualizing soil phase relationships (gravimetry). Part of the "Suite Geotécnica" from Universidad Pontificia Bolivariana.

## Tech Stack
- **Language**: Python 3.12
- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data**: Pandas, NumPy

## Project Structure
- `Gravimetria.py` — Main entry point with all app logic, UI, and inference engine
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — Streamlit server configuration (port 5000, host 0.0.0.0)

## Running the App
The app is configured to run via the "Start application" workflow:
```
streamlit run Gravimetria.py
```
It runs on port 5000 at 0.0.0.0.

## Features
- Inference engine that calculates all soil phase parameters from minimal inputs
- Phase diagrams showing Air, Water, and Solids components (Plotly)
- Two modes: Laboratorio (Laboratory) and Académico (Academic)
- Multiple unit systems (g, kg, N, kN, etc.)
- Report generation
