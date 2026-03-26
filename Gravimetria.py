import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Ronald Saenz – Gravimetría", layout="wide", page_icon="🏗️")

# 2. ENCABEZADO OPTIMIZADO
st.markdown("""
<div style="display:flex; align-items:center; padding:15px; border-bottom:3px solid #003087; margin-bottom:20px;">
    <div style="font-size:2rem; font-weight:800; color:#003087;">Ronald Saenz - <span style="color:#6b7280; font-size:1.2rem;">GRAVIMETRÍA</span></div>
</div>
""", unsafe_allow_html=True)

# 3. PANEL DE CONTROL
st.sidebar.title("👨‍🏫 Panel de Control")
modo = st.sidebar.radio("Modo:", ("Metas (Laboratorio)", "Académico (Base Vs=1)"))

u_peso = st.sidebar.selectbox("Unidad de Peso", ["g", "kg", "N", "kN"])
u_vol = st.sidebar.selectbox("Unidad de Volumen", ["cm³", "dm³ (L)", "m³"])
u_dens = st.sidebar.selectbox("Unidad de Densidad", ["g/cm³", "kN/m³", "kg/m³"])

# Factores de conversión
PESO_FACTOR = {"g": 1.0, "kg": 1e-3, "N": 9.80665e-3, "kN": 9.80665e-6}
VOL_FACTOR = {"cm³": 1.0, "dm³ (L)": 1e-3, "m³": 1e-6}
DENS_FACTOR = {"g/cm³": 1.0, "kN/m³": 9.80665, "kg/m³": 1e3}

fp, fv, fd = PESO_FACTOR[u_peso], VOL_FACTOR[u_vol], DENS_FACTOR[u_dens]

# 4. DIAGRAMA DE FASES LIGERO (Sin excesos de código)
def build_phase_diagram_light(f, gh, gd):
    vt = f["vt"] if f["vt"] > 0 else 1.0
    # Normalización de alturas
    y_s = f["vs"] / vt
    y_w = f["vw"] / vt
    y_a = f["va"] / vt

    fig = go.Figure()
    # Bloques de fases
    colors = {"s": "#8B5E3C", "w": "#4A90D9", "a": "#D6EAF8"}
    
    # Sólidos
    fig.add_trace(go.Bar(x=["Volumen"], y=[y_s], marker_color=colors["s"], name="Sólidos"))
    # Agua
    fig.add_trace(go.Bar(x=["Volumen"], y=[y_w], marker_color=colors["w"], name="Agua"))
    # Aire
    fig.add_trace(go.Bar(x=["Volumen"], y=[y_a], marker_color=colors["a"], name="Aire"))

    fig.update_layout(
        barmode='stack', height=400, showlegend=True,
        plot_bgcolor="white", margin=dict(t=20, b=20, l=10, r=10),
        yaxis=dict(showticklabels=False), xaxis=dict(title="Fases del Suelo")
    )
    return fig

# 5. LÓGICA DE CÁLCULO (Tu motor de 300 iteraciones simplificado para estabilidad)
diccionario_maestro = {"gs":"Gs","e":"e","n":"n","w":"w","s":"S","wm":"Wt","ws":"Ws","ww":"Ww","vt":"Vt","vs":"Vs","vv":"Vv","vw":"Vw","va":"Va","gh":"γh","gd":"γd"}

st.subheader("📥 Entrada de Datos")
seleccionados = st.multiselect("Variables conocidas:", list(diccionario_maestro.keys()), format_func=lambda x: diccionario_maestro[x])

inputs_dict = {}
if seleccionados:
    cols = st.columns(len(seleccionados))
    for i, clave in enumerate(seleccionados):
        inputs_dict[clave] = cols[i].number_input(f"{diccionario_maestro[clave]}", value=0.0, format="%.4f")

if st.button("🚀 Calcular"):
    d = {k: 0.0 for k in diccionario_maestro.keys()}
    if modo == "Académico (Base Vs=1)": d["vs"] = 1.0
    for k, v in inputs_dict.items():
        d[k] = v / 100.0 if k in ["w", "n", "s"] and v > 1.0 else v

    # Motor de inferencia (Versión estable)
    for _ in range(100):
        prev = d.copy()
        if d["gs"] > 0 and d["ws"] > 0 and d["vs"] == 0: d["vs"] = d["ws"] / d["gs"]
        if d["gs"] > 0 and d["vs"] > 0 and d["ws"] == 0: d["ws"] = d["gs"] * d["vs"]
        if d["ws"] > 0 and d["ww"] > 0 and d["wm"] == 0: d["wm"] = d["ws"] + d["ww"]
        if d["wm"] > 0 and d["ws"] > 0 and d["ww"] == 0: d["ww"] = d["wm"] - d["ws"]
        if d["ww"] > 0: d["vw"] = d["ww"]
        if d["vs"] > 0 and d["vv"] > 0: d["vt"] = d["vs"] + d["vv"]
        if d["vt"] > 0 and d["vs"] > 0: d["vv"] = d["vt"] - d["vs"]
        if d == prev: break

    d["va"] = max(d["vv"] - d["vw"], 0)
    gamma_h = d["wm"] / d["vt"] if d["vt"] > 0 else 0
    gamma_d = d["ws"] / d["vt"] if d["vt"] > 0 else 0
    
    st.session_state["resultado"] = (d, gamma_h, gamma_d)

# 6. RESULTADOS
if "resultado" in st.session_state:
    res, gh, gd = st.session_state["resultado"]
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.plotly_chart(build_phase_diagram_light(res, gh, gd), use_container_width=True)
    
    with col_b:
        st.write("### Resultados")
        res_df = pd.DataFrame({
            "Variable": ["e", "n%", "S%", "w%", "γh", "γd"],
            "Valor": [f"{res['e']:.4f}", f"{res['n']*100:.2f}%", f"{res['s']*100:.2f}%", 
                      f"{res['w']*100:.2f}%", f"{gh*fd:.2f}", f"{gd*fd:.2f}"]
        })
        st.table(res_df)
        
