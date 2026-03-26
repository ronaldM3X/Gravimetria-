import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import base64, io

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ronald Saenz – Gravimetría", layout="wide", page_icon="🏗️"
)

# 1. FUNCIÓN PARA REINICIAR (Ponla arriba, cerca de las configuraciones)
def reiniciar_valores():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# 2. BOTÓN DE REINICIO EN LA BARRA LATERAL
if st.sidebar.button("♻️ Reiniciar Todo", on_click=reiniciar_valores):
    st.sidebar.success("Valores restablecidos")

# ... (Aquí iría tu lógica de cálculo) ...

# 3. SLIDERS PARA EL DIAGRAMA DE FASES (Dentro de la pestaña de cálculos o resultados)
st.markdown("### 🎚️ Ajuste Dinámico de Fases")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    # Slider para el volumen de sólidos (Vs)
    nuevo_vs = st.slider("Ajustar Vs", min_value=0.1, max_value=10.0, value=float(d.get('vs', 1.0)), step=0.1, key="slider_vs")
with col_s2:
    # Slider para el volumen de agua (Vw)
    nuevo_vw = st.slider("Ajustar Vw", min_value=0.0, max_value=10.0, value=float(d.get('vw', 0.5)), step=0.1, key="slider_vw")
with col_s3:
    # Slider para el volumen de aire (Va)
    nuevo_va = st.slider("Ajustar Va", min_value=0.0, max_value=10.0, value=float(d.get('va', 0.2)), step=0.1, key="slider_va")

# Actualizamos los valores del diccionario antes de dibujar el gráfico
d['vs'], d['vw'], d['va'] = nuevo_vs, nuevo_vw, nuevo_va
d['vv'] = d['vw'] + d['va']
d['vt'] = d['vs'] + d['vv']

# 4. DIBUJAR EL GRÁFICO (Con la KEY única para evitar el error anterior)
st.plotly_chart(fig2, use_container_width=True, key="diagrama_dinamico_final")

# ─────────────────────────────────────────────────────────────────────────────
# 2. LOGO UPB + ENCABEZADO
# ─────────────────────────────────────────────────────────────────────────────
def get_logo_b64():
    for fname in ["assets/upb_logo2.png", "assets/upb_logo.png"]:
        try:
            with open(fname, "rb") as f:
                return base64.b64encode(f.read()).decode(), fname
        except Exception:
            continue
    return None, None


logo_b64, logo_fname = get_logo_b64()
if logo_b64:
    mime = "image/svg+xml" if logo_fname and logo_fname.endswith(".svg") else "image/png"
    logo_html = f'<img src="data:{mime};base64,{logo_b64}" style="height:90px; margin-right:24px; vertical-align:middle;">'
else:
    logo_html = '<span style="font-size:3rem; margin-right:16px; vertical-align:middle;">🏛️</span>'

st.markdown(
    f"""
<div style="display:flex; align-items:center; padding:18px 0 8px 0; border-bottom:3px solid #003087; margin-bottom:18px;">
    {logo_html}
    <div>
        <div style="font-size:2.4rem; font-weight:800; color:#003087; line-height:1.1; letter-spacing:-0.5px;">Ronald Saenz</div>
        <div style="font-size:1.25rem; font-weight:500; color:#6b7280; letter-spacing:2px; margin-top:2px;">GRAVIMETRÍA</div>
        <div style="font-size:0.78rem; color:#9ca3af; margin-top:2px;">Universidad Pontificia Bolivariana · Suite Geotécnica</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. PANEL DE CONTROL (SIDEBAR)
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("👨‍🏫 Panel de Control")
modo = st.sidebar.radio(
    "Selecciona el Modo:", ("Metas (Laboratorio)", "Académico (Base Vs=1)")
)
st.sidebar.markdown("---")

# ── SELECTOR DE UNIDADES ──────────────────────────────────────────────────────
st.sidebar.subheader("⚖️ Unidades")
u_peso = st.sidebar.selectbox("Unidad de Peso", ["g", "kg", "N", "kN"], index=0)
u_vol = st.sidebar.selectbox("Unidad de Volumen", ["cm³", "dm³ (L)", "m³"], index=0)
u_dens = st.sidebar.selectbox(
    "Unidad de Densidad / Peso Unitario", ["g/cm³", "kN/m³", "kg/m³"], index=0
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Los cálculos internos se realizan en g y cm³. Los resultados se convierten a la unidad seleccionada al mostrarlos."
)

# Factores de conversión (desde g o cm³ internos)
PESO_FACTOR = {"g": 1.0, "kg": 1e-3, "N": 9.80665e-3, "kN": 9.80665e-6}
VOL_FACTOR = {"cm³": 1.0, "dm³ (L)": 1e-3, "m³": 1e-6}
DENS_FACTOR = {"g/cm³": 1.0, "kN/m³": 9.80665, "kg/m³": 1e3}

fp = PESO_FACTOR[u_peso]
fv = VOL_FACTOR[u_vol]
fd = DENS_FACTOR[u_dens]


def fmt_peso(v):
    return f"{v * fp:.4f} {u_peso}"


def fmt_vol(v):
    return f"{v * fv:.4f} {u_vol}"


def fmt_dens(v):
    return f"{v * fd:.4f} {u_dens}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. DIAGRAMA DE FASES PROFESIONAL (función definida antes de usarla)
# ─────────────────────────────────────────────────────────────────────────────
def build_phase_diagram(f, gamma_h, gamma_d, u_vol, u_peso, u_dens, fv, fp, fd):
    vt = f["vt"] if f["vt"] > 0 else 1.0
    vs_n = f["vs"] / vt
    vw_n = f["vw"] / vt
    va_n = f["va"] / vt

    y_s_bot, y_s_top = 0.0, vs_n
    y_w_bot, y_w_top = vs_n, vs_n + vw_n
    y_a_bot, y_a_top = vs_n + vw_n, 1.0

    wt = f["wm"] if f["wm"] > 0 else 1e-9
    ws_n = f["ws"] / wt
    ww_n = f["ww"] / wt if wt > 0 else 0

    COL_W = 0.28
    COL_P = 0.28
    GAP = 0.08
    X_VOL = 0.12
    X_PES = X_VOL + COL_W + GAP
    ANN_L = 0.02
    ANN_R = X_PES + COL_P + 0.02

    C_SOLIDOS = "#8B5E3C"
    C_AGUA = "#4A90D9"
    C_AIRE = "#D6EAF8"
    C_BORDE = "#2C3E50"

    shapes = []
    annotations = []

    shapes.append(
        dict(
            type="rect",
            x0=X_VOL,
            x1=X_VOL + COL_W,
            y0=y_s_bot,
            y1=y_s_top,
            fillcolor=C_SOLIDOS,
            line=dict(color=C_BORDE, width=1.5),
        )
    )
    shapes.append(
        dict(
            type="rect",
            x0=X_VOL,
            x1=X_VOL + COL_W,
            y0=y_w_bot,
            y1=y_w_top,
            fillcolor=C_AGUA,
            line=dict(color=C_BORDE, width=1.5),
        )
    )
    shapes.append(
        dict(
            type="rect",
            x0=X_VOL,
            x1=X_VOL + COL_W,
            y0=y_a_bot,
            y1=y_a_top,
            fillcolor=C_AIRE,
            line=dict(color=C_BORDE, width=1.5),
        )
    )

    shapes.append(
        dict(
            type="rect",
            x0=X_PES,
            x1=X_PES + COL_P,
            y0=y_s_bot,
            y1=y_s_top,
            fillcolor=C_SOLIDOS,
            line=dict(color=C_BORDE, width=1.5),
        )
    )
    shapes.append(
        dict(
            type="rect",
            x0=X_PES,
            x1=X_PES + COL_P,
            y0=y_w_bot,
            y1=y_w_top,
            fillcolor=C_AGUA,
            line=dict(color=C_BORDE, width=1.5),
        )
    )
    shapes.append(
        dict(
            type="rect",
            x0=X_PES,
            x1=X_PES + COL_P,
            y0=y_a_bot,
            y1=y_a_top,
            fillcolor="white",
            line=dict(color=C_BORDE, width=1.5, dash="dot"),
        )
    )

    shapes.append(
        dict(
            type="line",
            x0=X_VOL,
            x1=X_VOL + COL_W,
            y0=vs_n,
            y1=vs_n,
            line=dict(color=C_BORDE, width=2),
        )
    )

    cx_vol = X_VOL + COL_W / 2
    if va_n > 0.04:
        annotations.append(
            dict(
                x=cx_vol,
                y=(y_a_bot + y_a_top) / 2,
                text=f"<b>AIRE</b><br>Va={f['va'] * fv:.3f} {u_vol}",
                showarrow=False,
                font=dict(size=12, color="#1a5276"),
                align="center",
            )
        )
    if vw_n > 0.04:
        annotations.append(
            dict(
                x=cx_vol,
                y=(y_w_bot + y_w_top) / 2,
                text=f"<b>AGUA</b><br>Vw={f['vw'] * fv:.3f} {u_vol}",
                showarrow=False,
                font=dict(size=12, color="white"),
                align="center",
            )
        )
    if vs_n > 0.04:
        annotations.append(
            dict(
                x=cx_vol,
                y=(y_s_bot + y_s_top) / 2,
                text=f"<b>SÓLIDOS</b><br>Vs={f['vs'] * fv:.3f} {u_vol}",
                showarrow=False,
                font=dict(size=12, color="white"),
                align="center",
            )
        )

    cx_pes = X_PES + COL_P / 2
    if va_n > 0.04:
        annotations.append(
            dict(
                x=cx_pes,
                y=(y_a_bot + y_a_top) / 2,
                text="<b>W = 0</b>",
                showarrow=False,
                font=dict(size=11, color="#7f8c8d"),
                align="center",
            )
        )
    if ww_n > 0.04:
        annotations.append(
            dict(
                x=cx_pes,
                y=(y_w_bot + y_w_top) / 2,
                text=f"<b>AGUA</b><br>Ww={f['ww'] * fp:.3f} {u_peso}",
                showarrow=False,
                font=dict(size=12, color="white"),
                align="center",
            )
        )
    if ws_n > 0.04:
        annotations.append(
            dict(
                x=cx_pes,
                y=(y_s_bot + y_s_top) / 2,
                text=f"<b>SÓLIDOS</b><br>Ws={f['ws'] * fp:.3f} {u_peso}",
                showarrow=False,
                font=dict(size=12, color="white"),
                align="center",
            )
        )

    ann_x = ANN_L

    def bracket_ann(y0, y1, label, color="#2c3e50"):
        mid = (y0 + y1) / 2
        shapes.append(
            dict(
                type="line",
                x0=ann_x + 0.03,
                x1=ann_x + 0.03,
                y0=y0,
                y1=y1,
                line=dict(color=color, width=2),
            )
        )
        shapes.append(
            dict(
                type="line",
                x0=ann_x + 0.03,
                x1=X_VOL,
                y0=y0,
                y1=y0,
                line=dict(color=color, width=1.5),
            )
        )
        shapes.append(
            dict(
                type="line",
                x0=ann_x + 0.03,
                x1=X_VOL,
                y0=y1,
                y1=y1,
                line=dict(color=color, width=1.5),
            )
        )
        annotations.append(
            dict(
                x=ann_x,
                y=mid,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=11, color=color),
                xanchor="right",
            )
        )

    if va_n > 0.01:
        bracket_ann(y_a_bot, y_a_top, f"Va<br>{f['va'] * fv:.3f} {u_vol}", "#1a5276")
    if (va_n + vw_n) > 0.01:
        bracket_ann(vs_n, 1.0, f"Vv<br>{f['vv'] * fv:.3f} {u_vol}", "#117864")
    if vw_n > 0.01:
        bracket_ann(y_w_bot, y_w_top, f"Vw<br>{f['vw'] * fv:.3f} {u_vol}", "#154360")
    annotations.append(
        dict(
            x=ann_x,
            y=(y_s_bot + y_s_top) / 2,
            text=f"<b>Vs</b><br>{f['vs'] * fv:.3f} {u_vol}",
            showarrow=False,
            font=dict(size=11, color="#6e2f1a"),
            xanchor="right",
        )
    )

    shapes.append(
        dict(
            type="line",
            x0=ann_x - 0.01,
            x1=ann_x - 0.01,
            y0=0,
            y1=1,
            line=dict(color="#2c3e50", width=2.5),
        )
    )
    shapes.append(
        dict(
            type="line",
            x0=ann_x - 0.01,
            x1=ann_x + 0.01,
            y0=0,
            y1=0,
            line=dict(color="#2c3e50", width=2),
        )
    )
    shapes.append(
        dict(
            type="line",
            x0=ann_x - 0.01,
            x1=ann_x + 0.01,
            y0=1,
            y1=1,
            line=dict(color="#2c3e50", width=2),
        )
    )
    annotations.append(
        dict(
            x=ann_x - 0.04,
            y=0.5,
            text=f"<b>Vt</b><br>{f['vt'] * fv:.3f} {u_vol}",
            showarrow=False,
            font=dict(size=12, color="#1b2631"),
            xanchor="right",
        )
    )

    ann_rx = ANN_R + 0.05

    def bracket_ann_r(y0, y1, label, color="#2c3e50"):
        mid = (y0 + y1) / 2
        shapes.append(
            dict(
                type="line",
                x0=ann_rx - 0.03,
                x1=ann_rx - 0.03,
                y0=y0,
                y1=y1,
                line=dict(color=color, width=2),
            )
        )
        shapes.append(
            dict(
                type="line",
                x0=X_PES + COL_P,
                x1=ann_rx - 0.03,
                y0=y0,
                y1=y0,
                line=dict(color=color, width=1.5),
            )
        )
        shapes.append(
            dict(
                type="line",
                x0=X_PES + COL_P,
                x1=ann_rx - 0.03,
                y0=y1,
                y1=y1,
                line=dict(color=color, width=1.5),
            )
        )
        annotations.append(
            dict(
                x=ann_rx,
                y=mid,
                text=f"<b>{label}</b>",
                showarrow=False,
                font=dict(size=11, color=color),
                xanchor="left",
            )
        )

    if ww_n > 0.01:
        bracket_ann_r(y_w_bot, y_w_top, f"Ww<br>{f['ww'] * fp:.3f} {u_peso}", "#154360")
    bracket_ann_r(y_s_bot, y_s_top, f"Ws<br>{f['ws'] * fp:.3f} {u_peso}", "#6e2f1a")

    shapes.append(
        dict(
            type="line",
            x0=ann_rx + 0.04,
            x1=ann_rx + 0.04,
            y0=0,
            y1=1,
            line=dict(color="#2c3e50", width=2.5),
        )
    )
    shapes.append(
        dict(
            type="line",
            x0=ann_rx + 0.02,
            x1=ann_rx + 0.04,
            y0=0,
            y1=0,
            line=dict(color="#2c3e50", width=2),
        )
    )
    shapes.append(
        dict(
            type="line",
            x0=ann_rx + 0.02,
            x1=ann_rx + 0.04,
            y0=1,
            y1=1,
            line=dict(color="#2c3e50", width=2),
        )
    )
    annotations.append(
        dict(
            x=ann_rx + 0.07,
            y=0.5,
            text=f"<b>Wt</b><br>{f['wm'] * fp:.3f} {u_peso}",
            showarrow=False,
            font=dict(size=12, color="#1b2631"),
            xanchor="left",
        )
    )

    annotations.append(
        dict(
            x=cx_vol,
            y=1.06,
            text="<b>VOLÚMENES</b>",
            showarrow=False,
            font=dict(size=14, color="#2c3e50"),
            xanchor="center",
        )
    )
    annotations.append(
        dict(
            x=cx_pes,
            y=1.06,
            text="<b>PESOS</b>",
            showarrow=False,
            font=dict(size=14, color="#2c3e50"),
            xanchor="center",
        )
    )

    formulas = [
        f"<b>e</b> = Vv/Vs = <b>{f['e']:.4f}</b>",
        f"<b>n</b> = Vv/Vt = <b>{f['n'] * 100:.2f}%</b>",
        f"<b>S</b> = Vw/Vv = <b>{f['s'] * 100:.2f}%</b>",
        f"<b>w</b> = Ww/Ws = <b>{f['w'] * 100:.2f}%</b>",
        f"<b>Gs</b> = Ws/Vs = <b>{f['gs']:.3f}</b>",
        f"<b>γh</b> = Wt/Vt = <b>{gamma_h * fd:.4f} {u_dens}</b>",
        f"<b>γd</b> = Ws/Vt = <b>{gamma_d * fd:.4f} {u_dens}</b>",
    ]
    annotations.append(
        dict(
            x=0.78,
            y=1.06,
            text="<b>Relaciones Fundamentales</b>",
            showarrow=False,
            font=dict(size=13, color="#003087"),
            xanchor="left",
        )
    )
    annotations.append(
        dict(
            x=0.78,
            y=0.5,
            text="<br>".join(formulas),
            showarrow=False,
            font=dict(size=11.5, color="#1b2631"),
            align="left",
            xanchor="left",
            bgcolor="#fdfefe",
            bordercolor="#aed6f1",
            borderwidth=1.5,
            borderpad=8,
        )
    )

    fig = go.Figure()
    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        height=520,
        margin=dict(l=10, r=10, t=60, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            range=[0, 1.05],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[-0.04, 1.12],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        showlegend=False,
        font=dict(family="Arial, sans-serif"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5. DICCIONARIO MAESTRO
# ─────────────────────────────────────────────────────────────────────────────
diccionario_maestro = {
    "gs": "Gs (Gravedad específica)",
    "e": "e (Relación de vacíos)",
    "n": "n (Porosidad %)",
    "w": "w (Contenido de humedad %)",
    "s": "S (Grado de saturación %)",
    "wm": "Wt (Peso total)",
    "ws": "Ws (Peso sólidos)",
    "ww": "Ww (Peso agua)",
    "vt": "Vt (Volumen total)",
    "vs": "Vs (Volumen sólidos)",
    "vv": "Vv (Volumen vacíos)",
    "vw": "Vw (Volumen agua)",
    "va": "Va (Volumen aire)",
    "gh": "γh (Unitario húmedo)",
    "gd": "γd (Unitario seco)",
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. PESTAÑAS PRINCIPALES
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs(["🧩 Gravimetría & Fases", "📥 Reporte Final"])

# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 1: GRAVIMETRÍA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("📥 1. Entrada de Datos Iniciales")

    # El multiselect va FUERA del form para que los campos aparezcan al seleccionar
    seleccionados = st.multiselect(
        "Variables conocidas:",
        options=list(diccionario_maestro.keys()),
        format_func=lambda x: diccionario_maestro[x],
        key="seleccionados",
    )

    # Los number_inputs y el botón van DENTRO del form para evitar rerenders parciales
    with st.form("calc_form"):
        inputs = {}
        if seleccionados:
            cols_in = st.columns(3)
            for i, clave in enumerate(seleccionados):
                inputs[clave] = cols_in[i % 3].number_input(
                    f"{diccionario_maestro[clave]}", value=0.0, format="%.4f", key=f"in_{clave}"
                )
        calcular = st.form_submit_button("🚀 Calcular Base")

    if calcular:
        inputs_real = {k: v for k, v in inputs.items()}
        st.session_state["debug_inputs"] = dict(inputs_real)

        tiene_peso = any(inputs_real.get(k, 0) > 0 for k in ["ws", "wm", "ww"])
        tiene_volumen = any(inputs_real.get(k, 0) > 0 for k in ["vs", "vt", "vv", "vw", "va"])

        if modo == "Metas (Laboratorio)" and not (tiene_peso or tiene_volumen):
            st.session_state["error_calculo"] = "❌ Datos insuficientes. Ingresa al menos un Peso (Ws, Wt o Ww) o un Volumen (Vs, Vt, Vv, Vw o Va) mayor a cero."
            if "resultado" in st.session_state:
                del st.session_state["resultado"]
        else:
            if "error_calculo" in st.session_state:
                del st.session_state["error_calculo"]

            d = {k: 0.0 for k in diccionario_maestro.keys()}
            if modo == "Académico (Base Vs=1)":
                d["vs"] = 1.0

            for k, v in inputs_real.items():
                d[k] = v / 100.0 if k in ["w", "n", "s"] and v > 1.0 else v

            # ── MOTOR DE INFERENCIA ──────────────────────────────────────────
            for _ in range(300):
                prev = dict(d)

                # --- Gs, Ws, Vs ---
                if d["gs"] > 0 and d["ws"] > 0 and d["vs"] == 0:
                    d["vs"] = d["ws"] / d["gs"]
                if d["gs"] > 0 and d["vs"] > 0 and d["ws"] == 0:
                    d["ws"] = d["gs"] * d["vs"]
                if d["ws"] > 0 and d["vs"] > 0 and d["gs"] == 0:
                    d["gs"] = d["ws"] / d["vs"]

                # --- Pesos: Wt = Ws + Ww ---
                if d["wm"] > 0 and d["ws"] > 0 and d["ww"] == 0:
                    d["ww"] = d["wm"] - d["ws"]
                if d["wm"] > 0 and d["ww"] > 0 and d["ws"] == 0:
                    d["ws"] = d["wm"] - d["ww"]
                if d["ws"] > 0 and d["ww"] > 0 and d["wm"] == 0:
                    d["wm"] = d["ws"] + d["ww"]

                # --- Humedad: w = Ww/Ws  →  Ws = Wt/(1+w), Ww = Wt*w/(1+w) ---
                if d["ws"] > 0 and d["w"] > 0 and d["ww"] == 0:
                    d["ww"] = d["ws"] * d["w"]
                if d["ws"] > 0 and d["ww"] > 0 and d["w"] == 0:
                    d["w"] = d["ww"] / d["ws"]
                if d["w"] > 0 and d["ww"] > 0 and d["ws"] == 0:
                    d["ws"] = d["ww"] / d["w"]
                # Wt + w conocidos → Ws
                if d["wm"] > 0 and d["w"] > 0 and d["ws"] == 0:
                    d["ws"] = d["wm"] / (1.0 + d["w"])
                # Ws + w conocidos → Wt
                if d["ws"] > 0 and d["w"] > 0 and d["wm"] == 0:
                    d["wm"] = d["ws"] * (1.0 + d["w"])

                # --- Vw = Ww (densidad agua = 1 g/cm³) ---
                if d["ww"] > 0 and d["vw"] == 0:
                    d["vw"] = d["ww"]
                if d["vw"] > 0 and d["ww"] == 0:
                    d["ww"] = d["vw"]

                # --- Saturación: S = Vw/Vv ---
                if d["vw"] > 0 and d["vv"] > 0 and d["s"] == 0:
                    d["s"] = d["vw"] / d["vv"]
                if d["s"] > 0 and d["vv"] > 0 and d["vw"] == 0:
                    d["vw"] = d["s"] * d["vv"]
                if d["s"] > 0 and d["vw"] > 0 and d["vv"] == 0:
                    d["vv"] = d["vw"] / d["s"]

                # --- Relación de vacíos: e = Vv/Vs ---
                if d["vv"] > 0 and d["vs"] > 0 and d["e"] == 0:
                    d["e"] = d["vv"] / d["vs"]
                if d["e"] > 0 and d["vs"] > 0 and d["vv"] == 0:
                    d["vv"] = d["e"] * d["vs"]
                if d["e"] > 0 and d["vv"] > 0 and d["vs"] == 0:
                    d["vs"] = d["vv"] / d["e"]

                # --- Porosidad: n = e/(1+e) = Vv/Vt ---
                if d["e"] > 0 and d["n"] == 0:
                    d["n"] = d["e"] / (1.0 + d["e"])
                if 0 < d["n"] < 1 and d["e"] == 0:
                    d["e"] = d["n"] / (1.0 - d["n"])
                if d["n"] > 0 and d["vt"] > 0 and d["vv"] == 0:
                    d["vv"] = d["n"] * d["vt"]
                if d["n"] > 0 and d["vt"] > 0 and d["vs"] == 0:
                    d["vs"] = (1.0 - d["n"]) * d["vt"]
                if d["n"] > 0 and d["vs"] > 0 and d["vt"] == 0:
                    d["vt"] = d["vs"] / (1.0 - d["n"])
                if d["n"] > 0 and d["vv"] > 0 and d["vt"] == 0:
                    d["vt"] = d["vv"] / d["n"]
                if d["vt"] > 0 and d["vv"] > 0 and d["n"] == 0:
                    d["n"] = d["vv"] / d["vt"]

                # --- Volúmenes: Vt = Vs + Vv ---
                if d["vt"] > 0 and d["vs"] > 0 and d["vv"] == 0:
                    d["vv"] = d["vt"] - d["vs"]
                if d["vt"] > 0 and d["vv"] > 0 and d["vs"] == 0:
                    d["vs"] = d["vt"] - d["vv"]
                if d["vs"] > 0 and d["vv"] > 0 and d["vt"] == 0:
                    d["vt"] = d["vs"] + d["vv"]

                # --- Vacíos: Vv = Vw + Va ---
                if d["vv"] > 0 and d["vw"] > 0 and d["va"] == 0:
                    d["va"] = d["vv"] - d["vw"]
                if d["vv"] > 0 and d["va"] > 0 and d["vw"] == 0:
                    d["vw"] = d["vv"] - d["va"]
                if d["vw"] > 0 and d["va"] > 0 and d["vv"] == 0:
                    d["vv"] = d["vw"] + d["va"]

                # --- Pesos unitarios: γh = Wt/Vt, γd = Ws/Vt ---
                if d["gh"] > 0 and d["vt"] > 0 and d["wm"] == 0:
                    d["wm"] = d["gh"] * d["vt"]
                if d["gd"] > 0 and d["vt"] > 0 and d["ws"] == 0:
                    d["ws"] = d["gd"] * d["vt"]
                if d["wm"] > 0 and d["vt"] > 0 and d["gh"] == 0:
                    d["gh"] = d["wm"] / d["vt"]
                if d["ws"] > 0 and d["vt"] > 0 and d["gd"] == 0:
                    d["gd"] = d["ws"] / d["vt"]

                # --- Relación S·e = w·Gs ---
                if d["gs"] > 0 and d["s"] > 0 and d["e"] > 0 and d["w"] == 0:
                    d["w"] = d["s"] * d["e"] / d["gs"]
                if d["gs"] > 0 and d["w"] > 0 and d["e"] > 0 and d["s"] == 0:
                    d["s"] = d["w"] * d["gs"] / d["e"]
                if d["gs"] > 0 and d["w"] > 0 and d["s"] > 0 and d["e"] == 0:
                    d["e"] = d["w"] * d["gs"] / d["s"]

                # --- γd = γh/(1+w) ---
                if d["gh"] > 0 and d["w"] > 0 and d["gd"] == 0:
                    d["gd"] = d["gh"] / (1.0 + d["w"])
                if d["gd"] > 0 and d["w"] > 0 and d["gh"] == 0:
                    d["gh"] = d["gd"] * (1.0 + d["w"])

                # --- γd = Gs·γw/(1+e) donde γw=1 ---
                if d["gs"] > 0 and d["e"] > 0 and d["gd"] == 0:
                    d["gd"] = d["gs"] / (1.0 + d["e"])
                if d["gd"] > 0 and d["gs"] > 0 and d["e"] == 0:
                    d["e"] = d["gs"] / d["gd"] - 1.0

                if d == prev:
                    break

            # ── VALORES FINALES DERIVADOS ─────────────────────────────────────
            if d["vv"] == 0 and d["vt"] > 0 and d["vs"] > 0:
                d["vv"] = d["vt"] - d["vs"]
            d["va"] = max(d["vv"] - d["vw"], 0)
            if d["wm"] == 0:
                d["wm"] = d["ws"] + d["ww"]

            gamma_h = d["wm"] / d["vt"] if d["vt"] > 0 else 0
            gamma_d = d["ws"] / d["vt"] if d["vt"] > 0 else 0

            st.session_state["resultado"] = d
            st.session_state["gamma_h"] = gamma_h
            st.session_state["gamma_d"] = gamma_d
            st.session_state["u_vol"] = u_vol
            st.session_state["u_peso"] = u_peso
            st.session_state["u_dens"] = u_dens
            st.session_state["fv"] = fv
            st.session_state["fp"] = fp
            st.session_state["fd"] = fd
            st.session_state["modo"] = modo

    # ── MOSTRAR ERROR SI LO HAY ───────────────────────────────────────────────
    if "error_calculo" in st.session_state:
        st.error(st.session_state["error_calculo"])

    # ── DEBUG: MOSTRAR INPUTS RECIBIDOS ──────────────────────────────────────
    if "debug_inputs" in st.session_state and st.session_state["debug_inputs"]:
        with st.expander("🔍 Diagnóstico — valores recibidos por el motor", expanded=True):
            di = st.session_state["debug_inputs"]
            if di:
                for k, v in di.items():
                    st.write(f"**{diccionario_maestro.get(k, k)}** → `{v}`")
            else:
                st.warning("El motor no recibió ningún valor. ¿Seleccionaste las variables y escribiste los datos?")

    # ── MOSTRAR RESULTADOS (fuera del bloque del botón) ───────────────────────
    
        # --- DICCIONARIO DE RESULTADOS (Ahora sí, con valores actualizados) ---
        resultados = {
            "Variable": [
                "Vs (Volumen sólidos)", "Vw (Volumen agua    # --- MOSTRAR RESULTADOS (Línea 814) ---
    if "resultado" in st.session_state:
        d = st.session_state["resultado"]
        gamma_h = st.session_state.get("gamma_h", 0)
        gamma_d = st.session_state.get("gamma_d", 0)

        st.markdown("---")
        st.subheader("📋 3. Tabla de Resultados")

        # --- SLIDERS DINÁMICOS ---
        st.markdown("### 🎚️ Ajuste Visual de Fases")
        c1, c2, c3 = st.columns(3)
        with c1:
            d["vs"] = st.slider("Vol. Sólido (Vs)", 0.1, 10.0, float(d.get("vs", 1.0)), key="s_vs")
        with c2:
            d["vw"] = st.slider("Vol. Agua (Vw)", 0.0, 10.0, float(d.get("vw", 0.5)), key="s_vw")
        with c3:
            d["va"] = st.slider("Vol. Aire (Va)", 0.0, 10.0, float(d.get("va", 0.2)), key="s_va")

        # Recalcular variables dependientes
        d["vv"] = d["vw"] + d["va"]
        d["vt"] = d["vs"] + d["vv"]
        d["e"] = d["vv"] / d["vs"] if d["vs"] > 0 else 0
        d["n"] = d["vv"] / d["vt"] if d["vt"] > 0 else 0
        d["s"] = d["vw"] / d["vv"] if d["vv"] > 0 else 0
)", "Va (Volumen aire)",
                "Vv (Volumen vacíos)", "Vt (Volumen total)",
                "Ws (Peso sólidos)", "Ww (Peso agua)", "Wt (Peso total)",
                "e (Relación de vacíos)", "n (Porosidad)",
                "S (Saturación)", "w (Humedad)", "Gs (Gravedad específica)",
                "γh (Unitario húmedo)", "γd (Unitario seco)",
            ],
            "Valor calculado": [
                fmt_vol(d["vs"]), fmt_vol(d["vw"]), fmt_vol(d["va"]),
                fmt_vol(d["vv"]), fmt_vol(d["vt"]),
                fmt_peso(d["ws"]), fmt_peso(d["ww"]), fmt_peso(d["wm"]),
                f"{d['e']:.4f}", f"{d['n'] * 100:.2f} %",
                f"{d['s'] * 100:.2f} %", f"{d['w'] * 100:.2f} %",
                f"{d['gs']:.4f}",
                fmt_dens(gamma_h), fmt_dens(gamma_d),
            ],
        }

        df_res = pd.DataFrame(resultados)
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        
# ══════════════════════════════════════════════════════════════════════════════
# PESTAÑA 2: REPORTE FINAL
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("📥 Reporte Final")
    if "resultado" not in st.session_state:
        st.info("ℹ️ Primero calcula los datos en la pestaña **Gravimetría & Fases**.")
    else:
        d = st.session_state["resultado"]
        gamma_h = st.session_state["gamma_h"]
        gamma_d = st.session_state["gamma_d"]
        _u_vol = st.session_state["u_vol"]
        _u_peso = st.session_state["u_peso"]
        _u_dens = st.session_state["u_dens"]
        _fv = st.session_state["fv"]
        _fp = st.session_state["fp"]
        _fd = st.session_state["fd"]

        def _fmt_vol(v): return f"{v * _fv:.4f} {_u_vol}"
        def _fmt_peso(v): return f"{v * _fp:.4f} {_u_peso}"
        def _fmt_dens(v): return f"{v * _fd:.4f} {_u_dens}"

        st.markdown("### Resumen de la muestra de suelo")
        col1, col2, col3 = st.columns(3)
        col1.metric("e (Relación de vacíos)", f"{d['e']:.4f}")
        col2.metric("n (Porosidad)", f"{d['n'] * 100:.2f} %")
        col3.metric("S (Saturación)", f"{d['s'] * 100:.2f} %")

        col4, col5, col6 = st.columns(3)
        col4.metric("w (Humedad)", f"{d['w'] * 100:.2f} %")
        col5.metric("Gs", f"{d['gs']:.4f}")
        col6.metric("γh", _fmt_dens(gamma_h))

        st.markdown("---")
        st.markdown("### Diagrama de Fases")
        if d["vs"] > 0 and d["vt"] > 0:
            fig2 = build_phase_diagram(d, gamma_h, gamma_d, _u_vol, _u_peso, _u_dens, _fv, _fp, _fd)
            st.plotly_chart(fig2, use_container_width=True, key="grafico_principal_unique")

        st.markdown("---")
        st.markdown("### Tabla completa de variables")
        resultados_rep = {
            "Variable": [
                "Vs", "Vw", "Va", "Vv", "Vt",
                "Ws", "Ww", "Wt",
                "e", "n", "S", "w", "Gs", "γh", "γd",
            ],
            "Descripción": [
                "Volumen sólidos", "Volumen agua", "Volumen aire",
                "Volumen vacíos", "Volumen total",
                "Peso sólidos", "Peso agua", "Peso total",
                "Relación de vacíos", "Porosidad", "Saturación",
                "Contenido de humedad", "Gravedad específica",
                "Peso unitario húmedo", "Peso unitario seco",
            ],
            "Valor": [
                _fmt_vol(d["vs"]), _fmt_vol(d["vw"]), _fmt_vol(d["va"]),
                _fmt_vol(d["vv"]), _fmt_vol(d["vt"]),
                _fmt_peso(d["ws"]), _fmt_peso(d["ww"]), _fmt_peso(d["wm"]),
                f"{d['e']:.4f}", f"{d['n'] * 100:.2f} %",
                f"{d['s'] * 100:.2f} %", f"{d['w'] * 100:.2f} %",
                f"{d['gs']:.4f}",
                _fmt_dens(gamma_h), _fmt_dens(gamma_d),
            ],
        }
        st.dataframe(pd.DataFrame(resultados_rep), use_container_width=True, hide_index=True)
