import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from calculos import load_data, calculate_buchholz, calculate_head_to_head, players

st.markdown(
    """
    <style>
        html, body, [data-testid="stApp"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(180deg, #a4cbef 0%, #2eb9ff 100%) !important;
            color: #222 !important;
            margin: 0;
            padding: 0;
        }
        .block-container {
            max-width: 90vw !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        /* Títulos principales */
        .main-title {
            text-align: center !important;
            font-size: 56px !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            text-shadow: 0 0 10px rgba(0,0,0,0.4) !important;
            margin-bottom: 0.3rem !important;
        }
        .subheader {
            text-align: center !important;
            font-size: 26px !important;
            font-weight: 600 !important;
            color: #e0f7ff !important;
            margin-bottom: 2rem !important;
        }
        /* Títulos de grupo */
        .group-title {
            color: #ffffff !important;
            background: linear-gradient(90deg, #1f4e79, #2eb9ff);
            text-align: center !important;
            margin: 1rem 0 0.5rem 0 !important;
            font-weight: bold !important;
            font-size: 20px !important;
            letter-spacing: 1px;
            border-radius: 12px;
            padding: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        /* Tabs */
        div[data-testid="stTabs"] button {
            background: #e6f4ff !important;
            border: none !important;
            color: #004080 !important;
            font-size: 20px !important;
            font-weight: 600 !important;
            padding: 8px 20px !important;
            margin: 0 8px !important;
            cursor: pointer !important;
            border-radius: 10px 10px 0 0 !important;
            transition: all 0.25s ease-in-out;
        }
        div[data-testid="stTabs"] button:hover {
            background: #b3e0ff !important;
            color: #003366 !important;
        }
        div[data-testid="stTabs"] button.active {
            background: #004080 !important;
            color: #fff !important;
        }
        /* Tablas modernas */
        table {
            border-radius: 12px !important;
            overflow: hidden !important;
            background: #ffffff !important;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
        }
        th {
            background: #2eb9ff !important;
            color: #fff !important;
            font-weight: 700 !important;
            text-transform: uppercase;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            border-bottom: 4px solid #2eb9ff !important;  /* o #ffd700 para dorado */
        }

                div[data-baseweb="tab-highlight"] {
            background-color: #2eb9ff !important;  /* cambia al color que quieras */
            height: 4px !important;               /* grosor de la raya */
            border-radius: 2px !important;        /* opcional: esquinas redondeadas */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Título con estilo limpio
st.markdown("<div class='main-title'>LIGA ONE PIECE MÁLAGA</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>6ª EDICIÓN</div>", unsafe_allow_html=True)

def highlight_top4(row):
    idx = row.name
    if idx < 4:
        return ['background-color: #d0f0ff; color: #004080; font-weight: bold;'] * len(row)
    return ['background-color: #f9fcff; color: #222;'] * len(row)

# Cargar datos desde calculos.py
group_tables, matches = load_data()

# Recalcular Buchholz y HeadToHead
for group, df in group_tables.items():
    group_players = set(df.index)
    group_matches = [m for m in matches if m[0] in group_players and m[1] in group_players]
    calculate_buchholz(df, group_matches)
    calculate_head_to_head(df, group_matches)

# Tabs
tab1, tab2 = st.tabs(["Clasificación", "Playoff"])

# TAB 1 - CLASIFICACIÓN
with tab1:
    col1, col2 = st.columns(2)

    for i, (group, df) in enumerate(group_tables.items()):
        df_display = df.copy()

        # Calcular Partidos Jugados
        df_display["Partidos Jugados"] = 0
        for _, row in df_display.iterrows():
            jugador = row.name
            df_display.loc[jugador, "Partidos Jugados"] = sum(
                1 for m in matches if jugador in m[:2]
            )

        df_display = df_display.sort_values(
            by=["Puntuación", "Buchholz", "HeadToHead", "Dif. de pts."],
            ascending=[False, False, False, False]
        ).reset_index()

        df_display.rename(columns={'index': 'Nombre'}, inplace=True)
        df_display['Puntuación'] = df_display['Puntuación'].astype(int)

        # Mostrar columnas seleccionadas
        columnas = ["Nombre", "Puntuación", "Partidos Jugados"]

        if i % 2 == 0:
            with col1:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[columnas].style.apply(highlight_top4, axis=1), hide_index=True)
        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[columnas].style.apply(highlight_top4, axis=1), hide_index=True)

# TAB 2 - PLAYOFF
# TAB 2 - PLAYOFF (animación reloj de arena)
with tab2:
    html = """
    <style>
    .sandglass-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 80vh;
        font-family: 'Segoe UI', sans-serif;
    }

    .hourglass {
        display: inline-block;
        position: relative;
        width: 64px;
        height: 64px;
    }

    .hourglass:after {
        content: " ";
        display: block;
        border-radius: 50%;
        width: 0;
        height: 0;
        margin: 6px;
        box-sizing: border-box;
        border: 26px solid #004080;
        border-color: #004080 transparent #004080 transparent;
        animation: hourglass 1.2s infinite;
    }

    @keyframes hourglass {
        0% {
            transform: rotate(0);
        }
        50% {
            transform: rotate(180deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    .sandglass-text {
        margin-top: 30px;
        font-size: 28px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 6px #000;
        text-align: center;
    }
    </style>

    <div class="sandglass-container">
        <div class="hourglass"></div>
        <div class="sandglass-text">⏳ Todavía por determinar</div>
    </div>
    """
    components.html(html, height=700)
