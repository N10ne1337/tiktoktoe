from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

board = [' ' for _ in range(9)]
difficulty = 1
improvement = 0

def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)

def check_draw(board):
    return ' ' not in board

def computer_move(board, difficulty):
    def minimax(board, depth, is_maximizing):
        if check_win(board, 'O'):
            return 1
        if check_win(board, 'X'):
            return -1
        if check_draw(board):
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'O'
                    score = minimax(board, depth + 1, False)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] == ' ':
                    board[i] = 'X'
                    score = minimax(board, depth + 1, True)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score

    best_move = None
    best_score = -float('inf')
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            score = minimax(board, 0, False)
            board[i] = ' '
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

@app.route('/')
def index():
    global board
    board = [' ' for _ in range(9)]  # Reset board on page load
    html_code = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Крестики-нолики</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { font-family: Arial, sans-serif; background-color: #2c2c2c; color: white; }
            .board { display: grid; grid-template-columns: repeat(3, 150px); grid-gap: 10px; margin: 20px auto; }
            .cell { width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; font-size: 3em; border: 1px solid #000; cursor: pointer; }
            .button { padding: 10px 20px; cursor: pointer; margin-top: 20px; }
            .container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
        </style>
        <script>
            function detectDevice() {
                const userAgent = navigator.userAgent || navigator.vendor || window.opera;
                if (/android/i.test(userAgent) || /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
                    document.body.style.zoom = "150%";
                }
            }

            function updateDifficultyInfo() {
                const difficultyNames = ["Самый легкий", "Легкий", "Средний", "Сложный", "Самый сложный"];
                const difficultyColors = ["light", "success", "warning", "danger", "dark"];
                document.getElementById('difficulty-info').innerHTML = `
                    <p>Текущая сложность: <span class="text-${difficultyColors[difficulty - 1]}">${difficultyNames[difficulty - 1]}</span></p>
                    <p>ИИ поумнел на ${improvement}%</p>
                `;
            }

            function updateDifficultyInfoModal() {
                const difficultyNames = ["Самый легкий", "Легкий", "Средний", "Сложный", "Самый сложный"];
                const difficultyColors = ["light", "success", "warning", "danger", "dark"];
                document.getElementById('difficulty-info-modal').innerHTML = `
                    <p>Текущая сложность: <span class="text-${difficultyColors[difficulty - 1]}">${difficultyNames[difficulty - 1]}</span></p>
                    <p>ИИ поумнел на ${improvement}%</p>
                `;
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
                        showModal(data.status);
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
                .then(response => response.json())
                .then(data => {
                    updateBoard(data.board);
                });
            }

            function showModal(status) {
                const modal = document.createElement('div');
                modal.style.position = 'fixed';
                modal.style.left = '0';
                modal.style.top = '0';
                modal.style.width = '100%';
                modal.style.height = '100%';
                modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                modal.style.display = 'flex';
                modal.style.alignItems = 'center';
                modal.style.justifyContent = 'center';
                modal.innerHTML = `
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center;">
                        <p>${status === 'win' ? 'Вы выиграли!' : status === 'lose' ? 'Вы проиграли!' : 'Ничья!'}</p>
                        <button class="btn btn-secondary" onclick="location.reload()">Играть заново</button>
                        <div id="difficulty-info-modal" class="mt-3"></div>
                    </div>
                `;
                document.body.appendChild(modal);
                updateDifficultyInfoModal();
            }

            document.addEventListener('DOMContentLoaded', () => {
                updateBoard([' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']);
                updateDifficultyInfo();
            });
        </script>
    </head>
    <body onload="detectDevice()">
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
                <div class="cell" id="{{ i }}" onclick="makeMove({{ i }})">{{ board[i] }}</div>
                {% endfor %}
            </div>
            <button class="btn btn-secondary button" onclick="resetGame()">Начать сначала</button>
            <div id="difficulty-info" class="mt-3"></div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_code, board=board)

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
