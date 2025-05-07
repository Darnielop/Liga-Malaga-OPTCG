import pandas as pd
import json
import shlex
import os

# Datos iniciales
players = {
    "Grupo 1": ["Bipi", "Remu", "Donete", "Grace", "Pablo Sanz", "Borja", "Juanje", "Joselu", "Javi Guerrero"],
    "Grupo 2": ["Jafervi", "Fita", "Rome", "Tony", "Dario", "Antonio Medina", "Soto", "Marco Calabrese", "Sergio"],
    "Grupo 3": ["Francis", "Pasku", "Kai", "Bloke", "Iñaki", "Ruben", "Manzanator", "Fran", "Rafa"],
    "Grupo 4": ["Marco", "Mario", "Nanaki", "Santi", "Seyok", "Kiyo", "Pablo Jamones", "Guille", "Xavi"]
}

DATA_FILE = 'resultados.json'

def initialize_table(players):
    return pd.DataFrame({
        'Victorias': 0,
        'Derrotas': 0,
        'Empates': 0,
        'Puntuación': 0.0,
        'Buchholz': 0,
        'Dif. de pts.': 0,
        'HeadToHead': 0
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

def register_result(df, p1, p2, score1, score2, matches):
    if any((p1 == m[0] and p2 == m[1]) or (p1 == m[1] and p2 == m[0]) for m in matches):
        print(f"⚠️ El resultado entre {p1} y {p2} ya fue registrado.")
        return

    winner = p1 if score1 > score2 else p2
    matches.append((p1, p2, score1, score2, winner))

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

    print(f"✅ Resultado registrado correctamente: {p1} {score1}-{score2} {p2}")

def calculate_buchholz(df, matches):
    for player in df.index:
        opponents = [p2 if p1 == player else p1 for m in matches if len(m) >= 4
                     for p1, p2 in [(m[0], m[1])] if p1 == player or p2 == player]
        df.loc[player, 'Buchholz'] = sum(df.loc[op, 'Puntuación'] for op in opponents if op in df.index)

def calculate_head_to_head(df, matches):
    h2h_matrix = {player: {} for player in df.index}
    for m in matches:
        if len(m) == 5:
            p1, p2, _, _, winner = m
            if winner == p1:
                h2h_matrix[p1][p2] = 1
                h2h_matrix[p2][p1] = 0
            else:
                h2h_matrix[p2][p1] = 1
                h2h_matrix[p1][p2] = 0

    for player in df.index:
        total = 0
        for other in df.index:
            if player == other:
                continue
            if df.loc[player, 'Puntuación'] == df.loc[other, 'Puntuación'] and \
               df.loc[player, 'Buchholz'] == df.loc[other, 'Buchholz']:
                total += h2h_matrix.get(player, {}).get(other, 0)
        df.loc[player, 'HeadToHead'] = total

def display_table(df, group_name):
    df.sort_values(by=['Puntuación', 'Buchholz', 'HeadToHead', 'Dif. de pts.'], ascending=[False, False, False, False], inplace=True)
    print(f"\n{group_name} - Tabla Final")
    print(df)

# Ejecutar
if __name__ == '__main__':
    group_tables, matches = load_data()

    while True:
        print("Introduce el resultado en el formato: \"Jugador_1\" \"Jugador_2\" Resultado_1 Resultado_2")
        print("Escribe 'fin' para terminar de introducir resultados.")
        entrada = input().strip()
        if entrada.lower() == 'fin':
            break
        try:
            tokens = shlex.split(entrada)
            if len(tokens) == 4:
                p1, p2, score1, score2 = tokens
                score1, score2 = int(score1), int(score2)
                found = False
                for group, df in group_tables.items():
                    if p1 in df.index and p2 in df.index:
                        register_result(df, p1, p2, score1, score2, matches)
                        found = True
                if not found:
                    print(f"⚠️ Jugadores no encontrados en el mismo grupo: {p1}, {p2}")
            else:
                print("Formato incorrecto. Asegúrate de usar comillas para nombres compuestos.")
        except ValueError:
            print("Formato incorrecto. Inténtalo de nuevo.")

    for group, df in group_tables.items():
        group_players = set(df.index)
        group_matches = [m for m in matches if m[0] in group_players and m[1] in group_players]
        calculate_buchholz(df, group_matches)
        calculate_head_to_head(df, group_matches)


    save_data(group_tables, matches)

    for group, df in group_tables.items():
        display_table(df, group)
