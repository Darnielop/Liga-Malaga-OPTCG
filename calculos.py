import pandas as pd
import json
import shlex
import os

# Datos iniciales
players = {
    "Grupo 1": ["Marco", "Fran", "Antonio Italiano", "Antonio Medina", "Bipi", "Bloque", "Borja", "Dario", "Donete"],
    "Grupo 2": ["Francis", "Iñaki", "Javi", "Joselu", "Kai", "Kiyo", "Manzanator", "Marco Calabrese", "Mario"],
    "Grupo 3": ["Pablo Sanz", "Rafa", "Sergio", "Seyok", "Tony", "Xavi", "Fita", "Grace", "Guille"],
    "Grupo 4": ["Juanje", "Javi Guerrero", "Rubén", "Santi", "Remu", "Nanaki", "Pablo Jamones", "Rome", "Pasku"]
}

# Guardar y cargar datos
DATA_FILE = 'resultados.json'

def initialize_table(players):
    return pd.DataFrame({
        'Victorias': 0,
        'Derrotas': 0,
        'Empates': 0,
        'Puntuación': 0.0,
        'Buchholz': 0,
        'Dif. de pts.': 0
    }, index=players)

def save_data(group_tables, matches):
    data = {group: df.to_dict() for group, df in group_tables.items()}
    with open(DATA_FILE, 'w') as f:
        json.dump({"tables": data, "matches": matches}, f)

def load_data():
    if not os.path.exists(DATA_FILE):
        print("📂 No se encontró 'resultados.json'. Se creará uno nuevo.")
        return {group: initialize_table(players[group]) for group in players}, []

    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        group_tables = {group: pd.DataFrame.from_dict(df) for group, df in data['tables'].items()}
        matches = data.get('matches', [])
        return group_tables, matches

    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ Error al cargar los datos. Se inicializarán nuevos datos.")
        return {group: initialize_table(players[group]) for group in players}, []

def register_result(df, p1, p2, score1, score2, team1, team2, matches):
    if any((p1 == m[0] and p2 == m[1]) or (p1 == m[1] and p2 == m[0]) for m in matches):
        print(f"⚠️ El resultado entre {p1} y {p2} ya fue registrado.")
        return

    matches.append((p1, p2, score1, score2, team1, team2))

    if score1 == 2 and score2 == 0:
        df.loc[p1, 'Victorias'] += 1
        df.loc[p2, 'Derrotas'] += 1
        df.loc[p1, 'Puntuación'] += 3
    elif score1 == 2 and score2 == 1:
        df.loc[p1, 'Victorias'] += 1
        df.loc[p2, 'Derrotas'] += 1
        df.loc[p1, 'Puntuación'] += 2
        df.loc[p2, 'Puntuación'] += 1
    elif score2 == 2 and score1 == 0:
        df.loc[p2, 'Victorias'] += 1
        df.loc[p1, 'Derrotas'] += 1
        df.loc[p2, 'Puntuación'] += 3
    elif score2 == 2 and score1 == 1:
        df.loc[p2, 'Victorias'] += 1
        df.loc[p1, 'Derrotas'] += 1
        df.loc[p2, 'Puntuación'] += 2
        df.loc[p1, 'Puntuación'] += 1

    print(f"✅ Resultado registrado correctamente: {p1} ({team1}) {score1}-{score2} {p2} ({team2})")

def calculate_buchholz(df, matches):
    for player in df.index:
        opponents = [p2 if p1 == player else p1 for p1, p2, _, _, _, _ in matches if p1 == player or p2 == player]
        df.loc[player, 'Buchholz'] = sum(df.loc[op, 'Puntuación'] for op in opponents)

def display_table(df, group_name):
    df.sort_values(by=['Puntuación', 'Buchholz', 'Dif. de pts.'], ascending=[False, False, False], inplace=True)
    print(f"\n{group_name} - Tabla Final")
    print(df)

group_tables, matches = load_data()

while True:
    print("Introduce el resultado en el formato: \"Jugador_1\" \"Jugador_2\" Resultado_1 Resultado_2 Equipo_1 Equipo_2")
    print("Escribe 'fin' para terminar de introducir resultados.")
    entrada = input().strip()
    if entrada.lower() == 'fin':
        break
    try:
        tokens = shlex.split(entrada)
        if len(tokens) == 6:
            p1, p2, score1, score2, team1, team2 = tokens
            score1, score2 = int(score1), int(score2)
            for group, df in group_tables.items():
                if p1 in df.index and p2 in df.index:
                    register_result(df, p1, p2, score1, score2, team1, team2, matches)
        else:
            print("Formato incorrecto. Asegúrate de usar comillas para nombres compuestos.")
    except ValueError:
        print("Formato incorrecto. Inténtalo de nuevo.")

for group, df in group_tables.items():
    calculate_buchholz(df, matches)

save_data(group_tables, matches)

for group, df in group_tables.items():
    display_table(df, group)