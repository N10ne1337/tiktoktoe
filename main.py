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
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { font-family: Arial, sans-serif; }
            .board { display: grid; grid-template-columns: repeat(3, 150px); grid-gap: 10px; margin: 20px auto; }
            .cell { width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; font-size: 3em; border: 1px solid #000; cursor: pointer; }
            #modal { display: none; position: fixed; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); align-items: center; justify-content: center; }
            .modal-content { background: white; padding: 20px; border-radius: 10px; text-align: center; }
            .button { padding: 10px 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container text-center">
            <h1 class="my-4">Крестики-нолики</h1>
            <div class="mb-4">
                <button class="btn btn-light" onclick="setDifficulty(1)">Самый легкий</button>
                <button class="btn btn-success" onclick="setDifficulty(2)">Легкий</button>
                <button class="btn btn-warning" onclick="setDifficulty(3)">Средний</button>
                <button class="btn btn-danger" onclick="setDifficulty(4)">Сложный</button>
                <button class="btn btn-dark" onclick="setDifficulty(5)">Самый сложный</button>
            </div>
            <div class="board mx-auto">
                {% for i in range(9) %}
                <div class="cell" id="{{ i }}" onclick="makeMove({{ i }})"></div>
                {% endfor %}
            </div>
            <div id="modal" class="d-flex">
                <div class="modal-content">
                    <p id="resultText"></p>
                    <button class="btn btn-secondary" onclick="resetGame()">Играть заново</button>
                </div>
            </div>
        </div>
        <script>
            let difficulty = 1; // Default difficulty

            function setDifficulty(level) {
                difficulty = level;
            }

            function makeMove(cell) {
                fetch('/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ move: cell, difficulty: difficulty })
                })
                .then(response => response.json())
                .then(data => {
                    updateBoard(data.board);
                    if (data.status === 'win' || data.status === 'lose' || data.status === 'draw') {
                        document.getElementById('resultText').innerText = data.status === 'win' ? 'Вы выиграли!' : data.status === 'lose' ? 'Вы проиграли!' : 'Ничья!';
                        document.getElementById('modal').style.display = 'flex';
                    }
                });
            }

            function updateBoard(board) {
                for (let i = 0; i < board.length; i++) {
                    document.getElementById(i.toString()).innerText = board[i];
                }
            }

            function resetGame() {
                fetch('/reset', { method: 'POST' })
                .then(() => {
                    updateBoard([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']);
                    document.getElementById('modal').style.display = 'none';
                });
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
