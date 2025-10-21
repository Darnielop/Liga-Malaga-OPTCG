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
            border-bottom: 4px solid #2eb9ff !important;
        }

        div[data-baseweb="tab-highlight"] {
            background-color: #2eb9ff !important;
            height: 4px !important;
            border-radius: 2px !important;
        }
        
        /* Estilos para apuestas */
        .betting-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #2eb9ff;
        }
        
        .odds-value {
            font-size: 32px;
            font-weight: 900;
            color: #ffd700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .winner-badge {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            display: inline-block;
            margin-left: 10px;
        }
        
        .eliminated-badge {
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            display: inline-block;
            margin-left: 10px;
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
tab1, tab2, tab3 = st.tabs(["Playoff", "Clasificación", "🎰 Apuestas"])

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
                st.dataframe(df_display[columnas].style.apply(highlight_top4, axis=1), hide_index=True)
        else:
            with col2:
                st.markdown(f"<div class='group-title'>{group}</div>", unsafe_allow_html=True)
                st.dataframe(df_display[columnas].style.apply(highlight_top4, axis=1), hide_index=True)

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

# TAB 3 - APUESTAS
with tab3:
    st.markdown("<div class='group-title'>🎰 CUOTAS PARA GANAR LA LIGA</div>", unsafe_allow_html=True)
    
    # Inicializar estado de apuestas si no existe
    if 'bets' not in st.session_state:
        st.session_state.bets = {}
    if 'total_bet' not in st.session_state:
        st.session_state.total_bet = 0
    if 'show_payment_modal' not in st.session_state:
        st.session_state.show_payment_modal = False
    if 'current_bet_player' not in st.session_state:
        st.session_state.current_bet_player = None
    if 'current_bet_amount' not in st.session_state:
        st.session_state.current_bet_amount = 0
    if 'current_bet_odds' not in st.session_state:
        st.session_state.current_bet_odds = 0
    
    # Jugadores clasificados a playoffs
    playoff_players = []
    player_stats = {}
    
    for group, df in group_tables.items():
        df_sorted = df.sort_values(
            by=["Puntuación", "Buchholz", "HeadToHead", "Dif. de pts."],
            ascending=[False, False, False, False]
        )
        
        for player in df_sorted.index[:4]:
            playoff_players.append(player)
            player_stats[player] = {
                'puntuacion': df_sorted.loc[player, 'Puntuación'],
                'buchholz': df_sorted.loc[player, 'Buchholz'],
                'victorias': df_sorted.loc[player, 'Victorias'],
                'dif_pts': df_sorted.loc[player, 'Dif. de pts.'],
                'grupo': group
            }
    
    # Ganadores confirmados de octavos (en cuartos)
    winners_octavos = ["Joselu", "Sergio", "Dani Estepona"]
    
    # Eliminados en octavos (perdedores)
    eliminated_players = ["Dario", "Juanje", "Ivan Martin"]
    
    # Filtrar solo jugadores activos
    active_players = [p for p in playoff_players if p not in eliminated_players]
    
    # Calcular cuotas (REDUCIDAS - factor de 2.5 en lugar de 5)
    def calculate_odds(player_name, stats, all_stats, is_winner=False):
        """
        Calcula cuotas más bajas basadas en rendimiento
        """
        if is_winner:
            base_score = stats['puntuacion'] * 0.4 + stats['buchholz'] * 0.2 + stats['dif_pts'] * 0.2 + stats['victorias'] * 0.2
            adjusted_score = base_score * 1.5  # 50% de bonus
        else:
            base_score = stats['puntuacion'] * 0.4 + stats['buchholz'] * 0.2 + stats['dif_pts'] * 0.2 + stats['victorias'] * 0.2
            adjusted_score = base_score * 0.85
        
        # Normalizar
        max_possible = max([s['puntuacion'] * 0.4 + s['buchholz'] * 0.2 + s['dif_pts'] * 0.2 + s['victorias'] * 0.2 for s in all_stats.values()])
        normalized = adjusted_score / max_possible if max_possible > 0 else 0
        
        # Convertir a cuota (REDUCIDO: factor 2.5 en lugar de 5)
        if normalized > 0:
            odds = (1 / normalized) * 2.5
            return max(1.2, min(odds, 15))  # Límites entre 1.2 y 15 (antes 1.5 y 50)
        return 15.0
    
    # Calcular todas las cuotas solo para jugadores activos
    odds_data = []
    for player in active_players:
        is_winner = player in winners_octavos
        odds = calculate_odds(player, player_stats[player], player_stats, is_winner)
        odds_data.append({
            'Jugador': player,
            'Cuota': odds,
            'Grupo': player_stats[player]['grupo'],
            'Puntos': int(player_stats[player]['puntuacion']),
            'Victorias': player_stats[player]['victorias'],
            'En Cuartos': is_winner
        })
    
    # Ordenar por cuota (favoritos primero)
    odds_df = pd.DataFrame(odds_data).sort_values('Cuota')
    
    # Modal de pago (estilo PayPal)
    if st.session_state.show_payment_modal:
        modal_overlay = st.container()
        with modal_overlay:
            st.markdown("""
            <style>
            .payment-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                z-index: 9998;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .payment-modal {
                background: white;
                border-radius: 20px;
                padding: 30px;
                max-width: 450px;
                width: 90%;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                z-index: 9999;
            }
            .payment-header {
                text-align: center;
                margin-bottom: 20px;
            }
            .payment-logo {
                font-size: 36px;
                color: #0070ba;
                font-weight: bold;
            }
            .payment-amount {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                margin: 20px 0;
            }
            .payment-amount h2 {
                margin: 0;
                font-size: 32px;
            }
            .payment-amount p {
                margin: 5px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='payment-modal'>
                <div class='payment-header'>
                    <div class='payment-logo'>Pago Seguro</div>
                    <p style='color: #666; margin: 10px 0;'>Apuesta: <strong>{st.session_state.current_bet_player}</strong></p>
                </div>
                <div class='payment-amount'>
                    <h2>€{st.session_state.current_bet_amount:.2f}</h2>
                    <p>Cuota: {st.session_state.current_bet_odds:.2f}x | Ganancia: €{st.session_state.current_bet_amount * st.session_state.current_bet_odds:.2f}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Datos de la Tarjeta")

            card_number = st.text_input("Número de tarjeta", placeholder="1234 5678 9012 3456", max_chars=19, key="card_number")
            
            col1, col2 = st.columns(2)
            with col1:
                expiry = st.text_input("Caducidad (MM/AA)", placeholder="12/25", max_chars=5, key="expiry")
            with col2:
                cvv = st.text_input("CVV", placeholder="123", max_chars=3, type="password", key="cvv")
            
            cardholder_name = st.text_input("Nombre del titular", placeholder="JUAN PEREZ", key="cardholder")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancelar", use_container_width=True, key="cancel_payment"):
                    st.session_state.show_payment_modal = False
                    st.rerun()
            
            with col2:
                if st.button("Confirmar Pago", use_container_width=True, type="primary", key="confirm_payment"):
                    # Validación básica
                    if card_number and expiry and cvv and cardholder_name:
                        if len(card_number.replace(" ", "")) >= 13 and len(cvv) == 3:
                            # Procesar apuesta
                            player = st.session_state.current_bet_player
                            amount = st.session_state.current_bet_amount
                            odds = st.session_state.current_bet_odds
                            
                            if player not in st.session_state.bets:
                                st.session_state.bets[player] = {'amount': 0, 'odds': odds}
                            
                            st.session_state.bets[player]['amount'] += amount
                            st.session_state.total_bet += amount
                            st.session_state.show_payment_modal = False
                            st.success(f"¡Pago procesado! Apuesta de €{amount:.2f} confirmada.")
                            st.rerun()
                        else:
                            st.error("Por favor, verifica los datos de la tarjeta")
                    else:
                        st.error("Completa todos los campos")
    
    # Panel de resumen de apuestas
    if not st.session_state.show_payment_modal:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1f4e79 0%, #2eb9ff 100%); 
                    padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center;'>
            <h2 style='color: white; margin: 0;'>Total Apostado: €{st.session_state.total_bet:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar jugadores activos en 2 columnas
        col1, col2 = st.columns(2)
        
        for idx, row in odds_df.iterrows():
            col = col1 if idx % 2 == 0 else col2
            
            with col:
                player_name = row['Jugador']
                winner_badge = "<span class='winner-badge'>EN CUARTOS</span>" if row['En Cuartos'] else ""
                
                st.markdown(f"""
                <div class='betting-card'>
                    <h3 style='margin:0; color:#004080;'>{player_name} {winner_badge}</h3>
                    <p style='margin:5px 0; color:#666; font-size:14px;'>{row['Grupo']} | {row['Puntos']} pts | {row['Victorias']} victorias</p>
                    <div style='text-align:center; margin-top:10px;'>
                        <span class='odds-value'>{row['Cuota']:.2f}</span>
                        <p style='margin:0; color:#888; font-size:12px;'>Cuota</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Simulador de apuesta
                bet_col1, bet_col2 = st.columns([2, 1])
                
                with bet_col1:
                    bet_amount = st.number_input(
                        f"Cantidad (€)",
                        min_value=0.0,
                        max_value=10000.0,
                        value=0.0,
                        step=10.0,
                        key=f"bet_{player_name}",
                        label_visibility="collapsed"
                    )
                
                with bet_col2:
                    if st.button("Apostar", key=f"btn_{player_name}", use_container_width=True):
                        if bet_amount > 0:
                            st.session_state.show_payment_modal = True
                            st.session_state.current_bet_player = player_name
                            st.session_state.current_bet_amount = bet_amount
                            st.session_state.current_bet_odds = row['Cuota']
                            st.rerun()
                        else:
                            st.warning("Introduce una cantidad mayor a 0")
                
                # Mostrar apuesta actual
                if player_name in st.session_state.bets and st.session_state.bets[player_name]['amount'] > 0:
                    current_bet = st.session_state.bets[player_name]['amount']
                    potential_win = current_bet * row['Cuota']
                    st.success(f"Apostado: €{current_bet:.2f} | Ganancia potencial: €{potential_win:.2f}")
        
        # Resumen de todas las apuestas
        if st.session_state.bets:
            st.markdown("---")
            st.markdown("<div class='group-title'>RESUMEN DE APUESTAS</div>", unsafe_allow_html=True)
            
            summary_data = []
            for player, bet_info in st.session_state.bets.items():
                if bet_info['amount'] > 0:
                    summary_data.append({
                        'Jugador': player,
                        'Apostado (€)': f"{bet_info['amount']:.2f}",
                        'Cuota': f"{bet_info['odds']:.2f}",
                        'Ganancia Potencial (€)': f"{bet_info['amount'] * bet_info['odds']:.2f}"
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, hide_index=True, use_container_width=True)
                
                # Botón para resetear apuestas
                if st.button("Limpiar todas las apuestas", type="secondary"):
                    st.session_state.bets = {}
                    st.session_state.total_bet = 0
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align:center; color:#ffffff; background:rgba(0,0,0,0.3); padding:15px; border-radius:10px;'>
            <p style='margin:0; font-size:14px;'>
                💡 <strong>La organización</strong> se reserva el derecho de modificar las cuotas y condiciones de las apuestas en cualquier momento.
            </p>
            <p style='margin:5px 0 0 0; font-size:12px; color:#e0f7ff;'>
            </p>
        </div>
        """, unsafe_allow_html=True)