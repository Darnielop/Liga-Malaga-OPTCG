import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

# CSS personalizado para mejorar la apariencia
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

# Título Principal
st.markdown("<div class='main-title'>LIGA ONE PIECE MÁLAGA</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>5ª EDICIÓN</div>", unsafe_allow_html=True)

# Cargar datos
with open("resultados.json", "r") as f:
    data = json.load(f)

# Tabs
tab1, tab2 = st.tabs(["Clasificación", "Playoff"])

# TAB 1 - CLASIFICACIÓN
with tab1:

    col1, col2 = st.columns(2)

    for i, (group, df) in enumerate(data['tables'].items()):
        df = pd.DataFrame.from_dict(df)[['Victorias', 'Derrotas', 'Puntuación', 'Buchholz', 'HeadToHead']]
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Nombre'}, inplace=True)

        # Ordenar con criterios: Puntuación, Buchholz, HeadToHead
        df = df[['Nombre', 'Puntuación', 'Buchholz', 'HeadToHead']].sort_values(
            by=['Puntuación', 'Buchholz', 'HeadToHead'], ascending=False).reset_index(drop=True)
        df['Puntuación'] = df['Puntuación'].astype(int)

        if i % 2 == 0:
            with col1:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df.drop(columns=["Buchholz", "HeadToHead"]).style.apply(highlight_top4, axis=1), hide_index=True)
        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df.drop(columns=["Buchholz", "HeadToHead"]).style.apply(highlight_top4, axis=1), hide_index=True)

with tab2:
    import streamlit.components.v1 as components

    top_16 = []
    for group, df in data['tables'].items():
        df = pd.DataFrame.from_dict(df)[['Puntuación', 'Buchholz', 'HeadToHead']]
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Nombre'}, inplace=True)
        df = df.sort_values(by=['Puntuación', 'Buchholz', 'HeadToHead'], ascending=False)
        top_16.extend(df['Nombre'].head(4).tolist())

    octavos = [
        (top_16[12], top_16[3]),
        (top_16[5], top_16[10]),
        (top_16[8], top_16[7]),
        (top_16[1], top_16[14]),
        (top_16[4], top_16[15]),
        (top_16[13], top_16[6]),
        (top_16[0], top_16[11]),
        (top_16[9], top_16[2]),
    ]

    html = """
    <style>
    .responsive-bracket {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 40px;
        padding: 20px;
        font-family: 'Segoe UI', sans-serif;
    }
    .bracket-title {
        text-align: center;
        color: white;
        font-size: 36px;
        margin-bottom: 20px;
        font-weight: bold;
        text-shadow: 2px 2px 10px #000;
    }
    .round-column {
        flex: 1 1 300px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        align-items: center;
    }
    .match-box {
        background: #004080;
        color: white;
        border: 2px solid #ffffff33;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        width: 100%;
        max-width: 260px;
        box-shadow: 0 0 8px #00ccff88;
        font-weight: bold;
        transition: 0.3s ease;
    }
    .match-box:hover {
        background: #007acc;
        transform: scale(1.03);
        box-shadow: 0 0 12px #00ffffaa;
    }
    </style>

    <div class="bracket-title">🏆 Playoffs - Octavos de Final</div>
    <div class="responsive-bracket">

        <div class="round-column">
    """

    # Lado izquierdo
    for i in range(4):
        a, b = octavos[i]
        html += f"""
            <div class="match-box">{a}<br><span style='color:#ccc'>vs</span><br>{b}</div>
        """

    html += """
        </div>

        <div class="round-column">
    """

    # Lado derecho
    for i in range(4, 8):
        a, b = octavos[i]
        html += f"""
            <div class="match-box">{a}<br><span style='color:#ccc'>vs</span><br>{b}</div>
        """

    html += """
        </div>
    </div>
    """

    components.html(html, height=2000)
