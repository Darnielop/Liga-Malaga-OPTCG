import streamlit as st
import pandas as pd
import json

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
            max-width: 1000px !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
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
            background: none !important;  /* Eliminar el fondo */
            border: none !important;  /* Eliminar el borde */
            color: #004080 !important;  /* Azul oscuro */
            font-size: 24px !important;  /* Tamaño de fuente */
            font-weight: bold !important;
            padding: 10px 15px !important;  /* Espaciado */
            margin: 0 15px !important;  /* Espaciado entre tabs */
            cursor: pointer !important;
            transition: all 0.3s ease-in-out !important;
            text-decoration: none !important; /* Eliminar cualquier subrayado */
            position: relative !important;  /* Permitir efectos visuales */
        }
        div[data-testid="stTabs"] button:hover {
            color: #ffffff !important;  /* Cambiar el color al pasar el ratón */
        }
        div[data-testid="stTabs"] button.active {
            color: #ffffff !important;  /* Cambiar el color del tab activo */
            background-color: #004080 !important;  /* Cambiar el fondo del tab activo */
            border-radius: 5px 5px 0 0 !important;  /* Redondear las esquinas superiores */
        }
        div[data-testid="stTabs"] button.active::before {
            content: "" !important;  /* Añadir un contenido antes del texto */
            position: absolute !important;  /* Posición absoluta */
            bottom: 0 !important;  /* Alinear con la parte inferior del tab */
            left: 0 !important;  /* Alinear con la parte izquierda del tab */
            width: 100% !important;  /* Ancho completo */
            height: 3px !important;  /* Grosor de la línea */
            background-color: #004080 !important;  /* Color de la línea */
            border-radius: 5px 5px 0 0 !important;  /* Redondear las esquinas superiores */
        }
        div[data-testid="stTabs"] button.active:hover {
            color: #ffffff !important;  /* Cambiar el color del tab activo al pasar el ratón */
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
tab1, tab2, tab3 = st.tabs(["Clasificación", "Meta", "Playoff"])

# TAB 1 - CLASIFICACIÓN
with tab1:

    col1, col2 = st.columns(2)

    for i, (group, df) in enumerate(data['tables'].items()):
        df = pd.DataFrame.from_dict(df)[['Victorias', 'Derrotas', 'Puntuación', 'Buchholz']]
        df.rename(columns={'Buchholz': 'Desempate'}, inplace=True)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Nombre'}, inplace=True)

        df = df[['Nombre', 'Victorias', 'Derrotas', 'Puntuación', 'Desempate']].sort_values(by=['Puntuación', 'Desempate'], ascending=False).reset_index(drop=True)
        df['Puntuación'] = df['Puntuación'].astype(int)

        if i % 2 == 0:
            with col1:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df.style.apply(highlight_top4, axis=1), hide_index=True)
        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df.style.apply(highlight_top4, axis=1), hide_index=True)

# TAB 2 - META
with tab2:
    team_stats = {}
    for match in data['matches']:
        _, _, score1, score2, team1, team2 = match
        if team1 not in team_stats:
            team_stats[team1] = {'Victorias': 0, 'Partidos': 0}
        if team2 not in team_stats:
            team_stats[team2] = {'Victorias': 0, 'Partidos': 0}
        team_stats[team1]['Partidos'] += 1
        team_stats[team2]['Partidos'] += 1
        if score1 > score2:
            team_stats[team1]['Victorias'] += 1
        else:
            team_stats[team2]['Victorias'] += 1

    meta_data = []
    for team, stats in team_stats.items():
        porcentaje_victorias = round((stats['Victorias'] / stats['Partidos']) * 100, 2)
        meta_data.append({
            'Nombre': team,
            'Partidos': stats['Partidos'],
            '% Victorias': porcentaje_victorias  # Guardamos como número para el orden correcto
        })

    winrate_df = pd.DataFrame(meta_data).sort_values('% Victorias', ascending=False).reset_index(drop=True)
    winrate_df['% Victorias'] = winrate_df['% Victorias'].astype(str) + '%'

    # Función para alternar colores en filas pares
    def highlight_rows(row):
        return ['background-color: #cfe2f3' if row.name % 2 == 0 else 'background-color: #ffffff'] * len(row)

    styled_df = winrate_df.style.apply(highlight_rows, axis=1).set_properties(**{
        'text-align': 'center',
        'border': '1px solid #000',
        'font-weight': 'bold',
        'color': '#000000',
    })

    st.dataframe(styled_df, hide_index=True)


# TAB 3 - PLAYOFF
with tab3:
    st.write("Aquí se mostrará el bracket de playoffs próximamente.")
