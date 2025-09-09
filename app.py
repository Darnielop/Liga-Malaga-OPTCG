import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from calculos import load_data, calculate_buchholz, calculate_head_to_head, players

# CSS personalizado
st.markdown(
    """
    <style>
        html, body, [data-testid="stApp"] {
            font-family: 'Inter', sans-serif;
            background: rgb(164,203,239) !important;
            background: linear-gradient(0deg, #8ecae8 0%, #2eb9ff 100%) !important;
            color: #333 !important;
            margin: 0;
            padding: 0;
        }
        .block-container {
            max-width: 100vw !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        .main-title {
            text-align: center !important;
            font-size: 60px !important;
            font-weight: bold !important;
            text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.5) !important;
            margin-bottom: 0.5rem !important;
            color: #ffffff !important;
        }
        .subheader {
            text-align: center !important;
            font-size: 30px !important;
            font-weight: bold !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5) !important;
            color: #ffffff !important;
            margin-bottom: 2rem !important;
        }
        .group-title {
            color: #ffffff !important;
            text-align: center !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            font-weight: bold !important;
            font-size: 20px !important;
            background-color: #1f4e79 !important;
            border-radius: 5px !important;
        }
        div[data-testid="stTabs"] button {
            background: none !important;
            border: none !important;
            color: #004080 !important;
            font-size: 24px !important;
            font-weight: bold !important;
            padding: 10px 15px !important;
            margin: 0 15px !important;
            cursor: pointer !important;
            transition: all 0.3s ease-in-out !important;
            text-decoration: none !important;
            position: relative !important;
        }
        div[data-testid="stTabs"] button:hover {
            color: #ffffff !important;
        }
        div[data-testid="stTabs"] button.active {
            color: #ffffff !important;
            background-color: #004080 !important;
            border-radius: 5px 5px 0 0 !important;
        }
        div[data-testid="stTabs"] button.active::before {
            content: "" !important;
            position: absolute !important;
            bottom: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 3px !important;
            background-color: #004080 !important;
            border-radius: 5px 5px 0 0 !important;
        }
        div[data-testid="stTabs"] button.active:hover {
            color: #ffffff !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def highlight_top4(row):
    idx = row.name
    return ['background-color: #cfe2f3; color: #000000; font-weight: bold; border: 1px solid #000;'] * len(row) if idx < 4 else ['background-color: #f0f8ff; color: #000000; border: 1px solid #000;'] * len(row)

# Título
st.markdown("<div class='main-title'>LIGA ONE PIECE MÁLAGA</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>6ª EDICIÓN</div>", unsafe_allow_html=True)

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
        df_display = df_display.sort_values(
            by=["Puntuación", "Buchholz", "HeadToHead", "Dif. de pts."],
            ascending=[False, False, False, False]
        ).reset_index()
        df_display.rename(columns={'index': 'Nombre'}, inplace=True)
        df_display['Puntuación'] = df_display['Puntuación'].astype(int)

        if i % 2 == 0:
            with col1:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[["Nombre", "Puntuación"]].style.apply(highlight_top4, axis=1), hide_index=True)
        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[["Nombre", "Puntuación"]].style.apply(highlight_top4, axis=1), hide_index=True)

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
