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
tab1, tab2 = st.tabs(["Playoff","Clasificación"])

# TAB 1 - CLASIFICACIÓN
with tab2:
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
        columnas = ["Nombre", "Partidos Jugados", "Puntuación"]

        if i % 2 == 0:
            with col1:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[columnas].style.apply(highlight_top4, axis=1), hide_index=True)
        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[columnas].style.apply(highlight_top4, axis=1), hide_index=True)

# TAB 2 - PLAYOFF

with tab1:
    # Obtener el top 4 de cada grupo ya ordenado
    top_16 = []
    for group, df in group_tables.items():
        df_display = df.copy()
        df_display = df_display.sort_values(
            by=["Puntuación", "Buchholz", "HeadToHead", "Dif. de pts."],
            ascending=[False, False, False, False]
        )
        top_16.extend(df_display.index[:4].tolist())

    # Emparejamientos (octavos de final)
    if len(top_16) >= 16:
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

        .bracket-bg {
            background: radial-gradient(circle at top, #003366 0%, #001f3f 60%, #000814 100%);
            padding: 40px 0;
            border-radius: 20px;
            box-shadow: inset 0 0 50px rgba(0,255,255,0.2);
            animation: pulseGlow 8s ease-in-out infinite alternate;
        }

        @keyframes pulseGlow {
            from { box-shadow: inset 0 0 50px rgba(0,255,255,0.15); }
            to { box-shadow: inset 0 0 80px rgba(46,185,255,0.4); }
        }

        .bracket-title {
            text-align: center;
            color: #00eaff;
            font-size: 46px;
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            text-shadow: 0 0 20px #00eaffaa, 0 0 40px #007bff77;
            margin-bottom: 40px;
            letter-spacing: 2px;
        }

        .responsive-bracket {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 60px;
            padding: 0 40px;
            font-family: 'Inter', sans-serif;
        }

        .round-column {
            flex: 1 1 320px;
            display: flex;
            flex-direction: column;
            gap: 24px;
            align-items: center;
        }

        .match-box {
            background: linear-gradient(145deg, #002b5c, #004c91);
            border: 2px solid rgba(0,255,255,0.3);
            border-radius: 14px;
            padding: 16px 20px;
            text-align: center;
            width: 100%;
            max-width: 280px;
            color: #ffffff;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-shadow: 0 0 5px rgba(0,0,0,0.5);
            box-shadow: 0 0 20px rgba(0,255,255,0.15);
            transition: all 0.25s ease-in-out;
            backdrop-filter: blur(4px);
        }

        .match-box:hover {
            background: linear-gradient(145deg, #007acc, #00bfff);
            border-color: #00eaff;
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0,255,255,0.5);
        }

        .vs {
            display: block;
            color: #00eaff;
            font-size: 16px;
            font-weight: 600;
            margin: 6px 0;
            text-shadow: 0 0 6px #00eaff77;
        }
        </style>

        <div class="bracket-bg">
            <div class="bracket-title">Playoffs - Cuartos de Final</div>
            <div class="responsive-bracket">

                <div class="round-column">
        """

        # Lado izquierdo
        for i in range(4):
            a, b = octavos[i]
            html += f"""
                <div class="match-box">{a}<span class="vs">VS</span>{b}</div>
            """

        html += """
                </div>
                <div class="round-column">
        """

        # Lado derecho
        for i in range(4, 8):
            a, b = octavos[i]
            html += f"""
                <div class="match-box">{a}<span class="vs">VS</span>{b}</div>
            """

        html += """
                </div>
            </div>
        </div>
        """

        components.html(html, height=1400)

    else:
        st.warning("⚠️ No hay suficientes jugadores para generar el cuadro de playoffs (se necesitan al menos 16).")
