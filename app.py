import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from calculos import load_data, calculate_buchholz, calculate_head_to_head, players

st.markdown("""
<style>

    /* ---- GENERAL ---- */
    html, body, [data-testid="stApp"] {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top, #0a2a43 0%, #071a29 40%, #05141f 100%) !important;
        color: #e8f5ff !important;
    }

    .block-container {
        max-width: 88vw !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* ---- TITULOS ---- */
    .main-title {
        text-align: center;
        font-size: 58px;
        font-weight: 900;
        background: linear-gradient(90deg, #4cc9ff, #00e0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 18px rgba(0,255,255,.4);
        margin-bottom: 0.3rem;
    }

    .subheader {
        text-align: center;
        font-size: 24px;
        font-weight: 500;
        color: #b1d8ff;
        letter-spacing: 3px;
        margin-bottom: 2rem;
    }

    /* ---- TARJETAS DE GRUPO ---- */
    .group-title {
        text-align: center;
        font-weight: bold;
        font-size: 22px;
        letter-spacing: 1px;
        color: #dff6ff;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        padding: 10px;
        margin-top: 1rem;
        box-shadow: 0 0 12px rgba(0, 170, 255, 0.3);
    }

    /* ---- TABS ---- */
    div[data-testid="stTabs"] button {
        background: #0f2437 !important;
        color: #7ac8ff !important;
        padding: 10px 22px !important;
        border-radius: 12px 12px 0 0 !important;
        border: none;
        font-size: 19px;
        font-weight: 600;
        transition: 0.3s;
        margin: 0 8px;
        box-shadow: inset 0 -2px 0 rgba(255,255,255,0.06);
    }

    div[data-testid="stTabs"] button:hover {
        background: #153149 !important;
        color: #b8e9ff !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        background: #1dafff !important;
        color: #002033 !important;
        font-weight: 700;
        box-shadow: 0 4px 16px rgba(0,255,255,0.4);
    }

    div[data-baseweb="tab-highlight"] {
        background-color: #00e0ff !important;
        height: 4px !important;
        border-radius: 4px !important;
    }

    /* Estilo para tablas generadas con st.table (SÍ funciona) */
    table {
        background: rgba(255,255,255,0.07) !important;
        backdrop-filter: blur(6px);
        border-radius: 14px !important;
        overflow: hidden !important;
        border-collapse: collapse !important;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
        width: 100% !important;
    }

    thead th {
        background: rgba(0,200,255,0.25) !important;
        color: #e7f8ff !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        padding: 12px !important;
        font-size: 14px !important;
    }

    tbody td {
        padding: 10px 14px !important;
        font-size: 15px !important;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        color: #e8faff !important;
        font-weight: 600;
    }

    /* Última fila sin borde */
    tbody tr:last-child td {
        border-bottom: none !important;
    }

    /* Hover suave */
    tbody tr:hover td {
        background: rgba(255,255,255,0.04) !important;
    }

    /* No clicable */
    table, th, td {
        pointer-events: none !important;
        user-select: none !important;
    }


</style>
""", unsafe_allow_html=True)

# Título con estilo limpio
st.markdown("<div class='main-title'>LIGA ONE PIECE MÁLAGA</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>7ª EDICIÓN</div>", unsafe_allow_html=True)

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

def tabla_clasificacion(df):
    html = """
    <style>
        .rank-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255,255,255,0.07);
            backdrop-filter: blur(6px);
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
        }

        .rank-table th {
            background: rgba(0,200,255,0.25);
            color: #e7f8ff;
            font-weight: 700;
            text-transform: uppercase;
            padding: 10px;
            font-size: 14px;
        }

        .rank-table td {
            padding: 10px 14px;
            font-size: 15px;
            color: #e8faff;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        .rank-table tr:last-child td {
            border-bottom: none;
        }

        .top4 {
            background: linear-gradient(90deg, rgba(0,208,255,0.2), rgba(0,234,255,0.13));
            font-weight: 800;
            color: #ffffff !important;
            text-shadow: 0 0 6px rgba(0,255,255,0.67);
        }
    </style>
    <table class='rank-table'>
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Puntuación</th>
                <th>Partidos</th>
            </tr>
        </thead>
        <tbody>
    """

    for i, row in df.iterrows():
        clase = "top4" if i < 4 else ""
        html += f"<tr class='{clase}'><td>{row['Nombre']}</td><td>{row['Puntuación']}</td><td>{row['Partidos Jugados']}</td></tr>"

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)

# Tabs
tab2, tab1 = st.tabs(["Clasificación","Playoff"])

# TAB 2 - CLASIFICACIÓN
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
                tabla_clasificacion(df_display)


        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                tabla_clasificacion(df_display)


# TAB 1 - PLAYOFF
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
    html = """
    <style>
    .loader-wrapper {
        height: 78vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadein 1.2s ease-in-out;
    }

    @keyframes fadein {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .spinner {
        width: 90px;
        height: 90px;
        border: 10px solid rgba(255, 255, 255, 0.3);
        border-top-color: #33bbff;
        border-radius: 50%;
        animation: spin 1.2s linear infinite;
        box-shadow: 0 0 15px rgba(0,0,0,0.25);
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .loader-text {
        margin-top: 25px;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 2px 2px 8px #000000aa;
        letter-spacing: 1px;
        text-align: center;
    }
    </style>

    <div class="loader-wrapper">
        <div class="spinner"></div>
        <div class="loader-text">Playoff<br>Disponible Próximamente</div>
    </div>
    """
    components.html(html, height=700)
