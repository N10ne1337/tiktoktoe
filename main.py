from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

# Инициализация пустого игрового поля
board = [' ' for _ in range(9)]

# Проверка победы
def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] == player:
            return True
    return False

# Проверка ничьи
def check_draw(board):
    return ' ' not in board

# Ход компьютера
def computer_move(board, difficulty):
    if difficulty == 1:  # Самый легкий уровень
        return random.choice([i for i, x in enumerate(board) if x == ' '])
    elif difficulty == 2:  # Легкий уровень
        return random.choice([i for i, x in enumerate(board) if x == ' '])
    elif difficulty == 3:  # Средний уровень
        return random.choice([i for i, x in enumerate(board) if x == ' '])
    elif difficulty == 4:  # Сложный уровень
        return random.choice([i for i, x in enumerate(board) if x == ' '])
    elif difficulty == 5:  # Самый сложный уровень
        return random.choice([i for i, x in enumerate(board) if x == ' '])

@app.route('/')
def index():
    html_code = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Крестики-нолики</title>
        <style>
            .board { display: grid; grid-template-columns: repeat(3, 100px); grid-gap: 5px; }
            .cell { width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 2em; border: 1px solid #000; }
        </style>
    </head>
    <body>
        <h1>Крестики-нолики</h1>
        <div class="board">
            <div class="cell" id="0" onclick="makeMove(0)"></div>
            <div class="cell" id="1" onclick="makeMove(1)"></div>
            <div class="cell" id="2" onclick="makeMove(2)"></div>
            <div class="cell" id="3" onclick="makeMove(3)"></div>
            <div class="cell" id="4" onclick="makeMove(4)"></div>
            <div class="cell" id="5" onclick="makeMove(5)"></div>
            <div class="cell" id="6" onclick="makeMove(6)"></div>
            <div class="cell" id="7" onclick="makeMove(7)"></div>
            <div class="cell" id="8" onclick="makeMove(8)"></div>
        </div>
        <script>
            let difficulty = prompt("Выберите уровень сложности (1-5):");

            function makeMove(cell) {
                fetch('/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ move: cell, difficulty: parseInt(difficulty) })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'win') {
                        alert('Вы выиграли!');
                    } else if (data.status === 'lose') {
                        alert('Вы проиграли!');
                    } else if (data.status === 'draw') {
                        alert('Ничья!');
                    }
                    updateBoard(data.board);
                });
            }

            function updateBoard(board) {
                for (let i = 0; i < board.length; i++) {
                    document.getElementById(i.toString()).innerText = board[i];
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_code)

@app.route('/move', methods=['POST'])
def move():
    global board
    data = request.get_json()
    player_move = data['move']
    difficulty = data['difficulty']
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

if __name__ == '__main__':
    app.run(debug=True)
