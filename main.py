from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

board = [' ' for _ in range(9)]

def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)

def check_draw(board):
    return ' ' not in board

def computer_move(board, difficulty):
    if difficulty == 1:  # Простой ИИ: случайный выбор
        return random.choice([i for i, x in enumerate(board) if x == ' '])
    # Для уровней 2, 3, 4, 5 можно добавить улучшенные алгоритмы ИИ
    return random.choice([i for i, x in enumerate(board) if x == ' '])

@app.route('/')
def index():
    return render_template_string(open('templates/index.html').read())

@app.route('/move', methods=['POST'])
def move():
    global board
    data = request.get_json()
    player_move = int(data['move'])
    difficulty = data['difficulty']
    if board[player_move] != ' ':
        return jsonify({'status': 'invalid', 'board': board})
    board[player_move] = 'X'
    if check_win(board, 'X'):
        return jsonify({'status': 'win', 'board': board})
    if check_draw(board):
        return jsonify({'status': 'draw', 'board': board})
    comp_move = computer_move(board, difficulty)
    board[comp_move] = 'O'
    if check_win(board, 'O'):
        return jsonify({'status': 'lose', 'board': board})
    if check_draw(board):
        return jsonify({'status': 'draw', 'board': board})
    return jsonify({'status': 'continue', 'board': board})

@app.route('/reset', methods=['POST'])
def reset():
    global board
    board = [' ' for _ in range(9)]
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)
