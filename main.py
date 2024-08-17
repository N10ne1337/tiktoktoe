from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Задайте свой секретный ключ для безопасности сессии

def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)

def check_draw(board):
    return ' ' not in board

def computer_move(board, difficulty):
    if difficulty == 1:
        # Простейший ИИ: случайный выбор доступного хода
        available_moves = [i for i, spot in enumerate(board) if spot == ' ']
        return random.choice(available_moves) if available_moves else None
    # Сложные уровни сложности пока что не реализованы
    return None

@app.route('/')
def index():
    session['board'] = [' ' for _ in range(9)]  # Сброс доски при каждой загрузке страницы
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
            function makeMove(cell) {
                fetch('/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ move: cell })
                })
                .then(response => response.json())
                .then(data => {
                    updateBoard(data.board);
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
        </script>
    </head>
    <body>
        <div class="container text-center">
            <h1 class="my-4">Крестики-нолики</h1>
            <div class="board mx-auto">
                {% for i in range(9) %}
                <div class="cell" id="{{ i }}" onclick="makeMove({{ i }})">{{ session['board'][i] }}</div>
                {% endfor %}
            </div>
            <button class="btn btn-secondary button" onclick="resetGame()">Начать сначала</button>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_code)

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    player_move = int(data['move'])
    board = session.get('board', [' ' for _ in range(9)])
    if board[player_move] != ' ':
        return jsonify({'status': 'invalid', 'board': board})
    board[player_move] = 'X'
    if check_win(board, 'X'):
        return jsonify({'status': 'win', 'board': board})
    if check_draw(board):
        return jsonify({'status': 'draw', 'board': board})
    comp_move = computer_move(board, 1)  # Пока что мы используем минимальную сложность
    if comp_move is not None:
        board[comp_move] = 'O'
    if check_win(board, 'O'):
        return jsonify({'status': 'lose', 'board': board})
    if check_draw(board):
        return jsonify({'status': 'draw', 'board': board})
    session['board'] = board
    return jsonify({'status': 'continue', 'board': board})

@app.route('/reset', methods=['POST'])
def reset():
    session['board'] = [' ' for _ in range(9)]
    return jsonify({'board': session['board']})

if __name__ == '__main__':
    app.run(debug=True)
