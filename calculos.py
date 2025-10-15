# -*- coding: utf-8 -*-
import pandas as pd
import json
import shlex
import os
from typing import Dict, List, Tuple

# -----------------------------------------------------------------------------
# Configuración inicial
# -----------------------------------------------------------------------------

# Mantener el sistema de puntuación actual (tal y como lo tienes):
#  - 2-0  -> ganador +5
#  - 2-1  -> ganador +3, perdedor +1
#  - 0-2  -> ganador +5
#  - 1-2  -> ganador +3, perdedor +1
#
# NOTA: Se asume formato al mejor de 3 (no hay empates).

players: Dict[str, List[str]] = {
    "Grupo 1": ["Jose Manzano", "Fran", "Juanje", "Donete", "Manzanator", "Ivan Martin", "Pasku", "Remu", "Grace"],
    "Grupo 2": ["Marco Calabrese", "Francis", "Bipi", "Ruben", "Marco", "Sergio", "Victor", "Soto", "Jota"],
    "Grupo 3": ["Mario", "Iñaki", "Joselu", "Borja", "Pablo Sanz", "Jorge Echeverria", "Silverify", "Miguel", "Jeb"],
    "Grupo 4": ["Seyok", "Dario", "Jafervi", "Fatty", "Rome", "Tony", "Bloke", "Dani Estepona", "Rafa"]
}

DATA_FILE = 'resultados.json'
COLUMNS = ['Victorias', 'Derrotas', 'Empates', 'Puntuación', 'Buchholz', 'Dif. de pts.', 'HeadToHead']

# -----------------------------------------------------------------------------
# Utilidades de inicialización / carga / guardado
# -----------------------------------------------------------------------------

def initialize_table(names: List[str]) -> pd.DataFrame:
    """Crea la tabla base para un grupo."""
    df = pd.DataFrame(0, index=names, columns=['Victorias', 'Derrotas', 'Empates', 'Dif. de pts.', 'HeadToHead'])
    df['Puntuación'] = 0.0
    df['Buchholz'] = 0.0
    # Reordena columnas
    df = df[['Victorias', 'Derrotas', 'Empates', 'Puntuación', 'Buchholz', 'Dif. de pts.', 'HeadToHead']]
    return df


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura que las columnas tengan el tipo numérico adecuado."""
    numeric_int = ['Victorias', 'Derrotas', 'Empates', 'Dif. de pts.', 'HeadToHead']
    numeric_float = ['Puntuación', 'Buchholz']

    for col in numeric_int:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0

    for col in numeric_float:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
        else:
            df[col] = 0.0

    # Orden fijo de columnas
    df = df[COLUMNS]
    return df


def _df_from_any(table_dict: dict) -> pd.DataFrame:
    """
    Reconstruye un DataFrame guardado en JSON, tanto si está orient='columns'
    (dict de columnas -> dict de índices) como orient='index' (dict de fila -> valores).
    """
    # Si las claves parecen columnas conocidas, asumimos orient='columns'.
    if set(table_dict.keys()) & set(COLUMNS):
        df = pd.DataFrame.from_dict(table_dict)
    else:
        df = pd.DataFrame.from_dict(table_dict, orient='index')
    df.index = df.index.astype(str)
    df = _coerce_types(df)
    return df


def save_data(group_tables: Dict[str, pd.DataFrame], matches: List[Tuple]) -> None:
    """Guarda tablas y partidos con orientación por índice para mayor robustez."""
    data = {group: df.to_dict(orient='index') for group, df in group_tables.items()}
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"tables": data, "matches": matches}, f, ensure_ascii=False, indent=2)


def load_data() -> Tuple[Dict[str, pd.DataFrame], List[Tuple]]:
    """Carga datos si existen; si no, inicializa desde cero."""
    if not os.path.exists(DATA_FILE):
        print("📂 No se encontró 'resultados.json'. Se creará uno nuevo.")
        return {group: initialize_table(players[group]) for group in players}, []

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruye cada tabla con tolerancia a distintos formatos previos
        group_tables = {}
        for group in players.keys():
            raw_tbl = data.get('tables', {}).get(group, {})
            if raw_tbl:
                df = _df_from_any(raw_tbl)
            else:
                df = initialize_table(players[group])

            # Garantiza que estén todos los jugadores del listado actual
            for name in players[group]:
                if name not in df.index:
                    df.loc[name] = 0
            df = _coerce_types(df)
            group_tables[group] = df

        matches = data.get('matches', [])
        return group_tables, matches

    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Error al cargar los datos. Se inicializarán nuevos datos.")
        return {group: initialize_table(players[group]) for group in players}, []


# -----------------------------------------------------------------------------
# Registro de resultados y cálculos auxiliares
# -----------------------------------------------------------------------------

def _valid_best_of_three(score1: int, score2: int) -> bool:
    """Valida marcadores válidos en BO3: {2-0, 2-1, 0-2, 1-2}."""
    valid = {(2, 0), (2, 1), (0, 2), (1, 2)}
    return (score1, score2) in valid


def register_result(df: pd.DataFrame, p1: str, p2: str, score1: int, score2: int, matches: List[Tuple]) -> None:
    """Registra un partido si no existe y actualiza métricas básicas."""
    # Evitar duplicados (independiente del orden)
    if any((p1 == m[0] and p2 == m[1]) or (p1 == m[1] and p2 == m[0]) for m in matches):
        print(f"⚠️ El resultado entre {p1} y {p2} ya fue registrado.")
        return

    # Validación de marcador
    if not _valid_best_of_three(score1, score2):
        print("⚠️ Marcador inválido. Usa BO3: 2-0, 2-1, 0-2 o 1-2.")
        return

    # Determinar ganador
    winner = p1 if score1 > score2 else p2
    matches.append((p1, p2, score1, score2, winner))

    # Actualizar diferencia de sets (ganados - perdidos)
    df.loc[p1, 'Dif. de pts.'] += (score1 - score2)
    df.loc[p2, 'Dif. de pts.'] += (score2 - score1)

    # Sistema de puntuación vigente (5/3/1)
    if score1 == 2 and score2 == 0:
        # Gana p1 2-0
        df.loc[p1, 'Victorias'] += 1
        df.loc[p2, 'Derrotas'] += 1
        df.loc[p1, 'Puntuación'] += 5
    elif score1 == 2 and score2 == 1:
        # Gana p1 2-1
        df.loc[p1, 'Victorias'] += 1
        df.loc[p2, 'Derrotas'] += 1
        df.loc[p1, 'Puntuación'] += 3
        df.loc[p2, 'Puntuación'] += 1
    elif score2 == 2 and score1 == 0:
        # Gana p2 2-0
        df.loc[p2, 'Victorias'] += 1
        df.loc[p1, 'Derrotas'] += 1
        df.loc[p2, 'Puntuación'] += 5
    elif score2 == 2 and score1 == 1:
        # Gana p2 2-1
        df.loc[p2, 'Victorias'] += 1
        df.loc[p1, 'Derrotas'] += 1
        df.loc[p2, 'Puntuación'] += 3
        df.loc[p1, 'Puntuación'] += 1

    print(f"✅ Resultado registrado correctamente: {p1} {score1}-{score2} {p2}")


def calculate_buchholz(df: pd.DataFrame, matches: List[Tuple]) -> None:
    """Calcula Buchholz como suma de puntos de los oponentes jugados en el grupo."""
    # Limpiar antes de recalcular
    df['Buchholz'] = 0.0
    for player in df.index:
        opponents = []
        for m in matches:
            if len(m) >= 4:
                p1, p2 = m[0], m[1]
                if p1 == player:
                    opponents.append(p2)
                elif p2 == player:
                    opponents.append(p1)
        df.loc[player, 'Buchholz'] = sum(float(df.loc[op, 'Puntuación']) for op in opponents if op in df.index)


def calculate_head_to_head(df: pd.DataFrame, matches: List[Tuple]) -> None:
    """
    Calcula HeadToHead sumando victorias directas SOLO entre jugadores que
    estén empatados en Puntuación y Buchholz.
    """
    # Construye matriz H2H
    h2h = {player: {} for player in df.index}
    for m in matches:
        if len(m) == 5:
            p1, p2, s1, s2, winner = m
            if winner == p1:
                h2h[p1][p2] = 1
                h2h[p2][p1] = 0
            else:
                h2h[p2][p1] = 1
                h2h[p1][p2] = 0

    # Reset antes de calcular
    df['HeadToHead'] = 0

    # Para cada jugador, suma victorias frente a rivales con los que
    # esté empatado en Puntuación y Buchholz
    for player in df.index:
        total = 0
        for other in df.index:
            if player == other:
                continue
            if (
                df.loc[player, 'Puntuación'] == df.loc[other, 'Puntuación'] and
                df.loc[player, 'Buchholz'] == df.loc[other, 'Buchholz']
            ):
                total += h2h.get(player, {}).get(other, 0)
        df.loc[player, 'HeadToHead'] = total


def display_table(df: pd.DataFrame, group_name: str) -> None:
    """Orden de desempate: Puntos > Buchholz > HeadToHead > Dif. de pts."""
    df = df.sort_values(
        by=['Puntuación', 'Buchholz', 'HeadToHead', 'Dif. de pts.'],
        ascending=[False, False, False, False]
    )
    print(f"\n{group_name} - Tabla Final")
    print(df)


# -----------------------------------------------------------------------------
# Ejecución interactiva
# -----------------------------------------------------------------------------

import re

if __name__ == '__main__':
    group_tables, matches = load_data()

    # Asegura tablas correctas
    for group, names in players.items():
        if group not in group_tables:
            group_tables[group] = initialize_table(names)
        else:
            for name in names:
                if name not in group_tables[group].index:
                    group_tables[group].loc[name] = 0
            group_tables[group] = _coerce_types(group_tables[group])

    print('Introduce resultados (ej: Dario 2 - 0 Rafa).')
    print("Puedes meter varios separados por saltos de línea. Escribe 'fin' para terminar.\n")

    while True:
        entrada = input().strip()
        if entrada.lower() == 'fin':
            break

        # Permitir pegar varias líneas a la vez
        lineas = entrada.splitlines()
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                continue

            # Regex para formato "Jugador1 X - Y Jugador2"
            m = re.match(r'^(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)$', linea)
            if not m:
                print(f"⚠️ Formato inválido: {linea}")
                continue

            p1, score1, score2, p2 = m.groups()
            score1, score2 = int(score1), int(score2)

            found = False
            for group, df in group_tables.items():
                if p1 in df.index and p2 in df.index:
                    register_result(df, p1, p2, score1, score2, matches)
                    found = True
                    break
            if not found:
                print(f"⚠️ Jugadores no encontrados en el mismo grupo: {p1}, {p2}")

    # Recalcular todo y mostrar
    for group, df in group_tables.items():
        group_players = set(df.index)
        group_matches = [m for m in matches if m[0] in group_players and m[1] in group_players]
        calculate_buchholz(df, group_matches)
        calculate_head_to_head(df, group_matches)

    save_data(group_tables, matches)
    for group, df in group_tables.items():
        display_table(df, group)
