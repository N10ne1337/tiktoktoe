from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def check_win(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)

def check_draw(board):
    return ' ' not in board

def minimax(board, depth, is_maximizing, alpha, beta):
    if check_win(board, 'O'):
        return 10 - depth
    elif check_win(board, 'X'):
        return depth - 10
    elif check_draw(board):
        return 0

    if is_maximizing:
        max_eval = -float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                eval = minimax(board, depth + 1, False, alpha, beta)
                board[i] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                eval = minimax(board, depth + 1, True, alpha, beta)
                board[i] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def computer_move(board, difficulty):
    def winning_move(board, player):
        for i in range(9):
            if board[i] == ' ':
                board[i] = player
                if check_win(board, player):
                    board[i] = ' '
                    return i
                board[i] = ' '
        return None

    available_moves = [i for i, spot in enumerate(board) if spot == ' ']

    if difficulty == 1:
        return random.choice(available_moves) if available_moves else None

    if difficulty == 2:
        move = winning_move(board, 'X')
        return move if move is not None else random.choice(available_moves)

    if difficulty == 3:
        move = winning_move(board, 'O')
        if move is not None:
            return move
        move = winning_move(board, 'X')
        return move if move is not None else random.choice(available_moves)

    if difficulty >= 4:
        best_score = -float('inf')
        best_move = None
        for i in available_moves:
            board[i] = 'O'
            score = minimax(board, 0, False, -float('inf'), float('inf'))
            board[i] = ' '
            if score > best_score:
                best_score = score
                best_move = i
        return best_move

    return None

@app.route('/')
def index():
    session['board'] = [' ' for _ in range(9)]
    session['difficulty'] = 1  # default difficulty
    return render_template_string(html_code)

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    player_move = int(data['move'])
    difficulty = int(data['difficulty'])
    board = session.get('board', [' ' for _ in range(9)])
    if board[player_move] == ' ':
        board[player_move] = 'X'
        if check_win(board, 'X'):
            session['board'] = board
            return jsonify({'status': 'win', 'board': board})
        if check_draw(board):
            session['board'] = board
            return jsonify({'status': 'draw', 'board': board})
        comp_move = computer_move(board, difficulty)
        if comp_move is not None:
            board[comp_move] = 'O'
            if check_win(board, 'O'):
                session['board'] = board
                return jsonify({'status': 'lose', 'board': board})
            if check_draw(board):
                session['board'] = board
                return jsonify({'status': 'draw', 'board': board})
        session['board'] = board
        return jsonify({'status': 'continue', 'board': board})
    return jsonify({'status': 'invalid', 'board': board})

@app.route('/reset', methods=['POST'])
def reset():
    session['board'] = [' ' for _ in range(9)]
    return jsonify({'board': session['board']})

html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Крестики-нолики</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: Arial, sans-serif; background-color: #2c2c2c; color: white; }
        .board { display: grid; grid-template-columns: repeat(3, 100px); grid-gap: 10px; margin: 20px auto; }
        .cell { width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 2em; border: 1px solid #000; cursor: pointer; background: white; color: black; }
        .button { padding: 10px 20px; cursor: pointer; margin-top: 20px; }
        .container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
        .difficulty { margin-bottom: 20px; }
    </style>
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const cells = document.querySelectorAll('.cell');
            cells.forEach(cell => {
                cell.addEventListener('click', function() {
                    if (this.textContent.trim() === '') {
                        makeMove(this.id);
                    }
                });
            });
        });

        function makeMove(cell) {
            const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
            fetch('/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ move: cell, difficulty: difficulty })
            })
            .then(response => response.json())
            .then(data => {
                updateBoard(data.board);
                if (data.status !== 'continue') {
                    showModal(data.status);
                }
            });
        }

        function updateBoard(board) {
            board.forEach((val, idx) => {
                document.getElementById(idx.toString()).textContent = val;
            });
        }

        function resetGame() {
            fetch('/reset', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                updateBoard(data.board);
            });
        }

        function showModal(status) {
            let message = '';
            if (status === 'win') {
                message = 'Поздравляем, вы выиграли!';
            } else if (status === 'lose') {
                message = 'Вы проиграли. Попробуйте снова!';
            } else if (status === 'draw') {
                message = 'Ничья!';
            }
            document.getElementById('resultMessage').textContent = message;
            $('#resultModal').modal('show');
        }
    </script>
</head>
<body>
    <div class="container text-center">
        <div class="difficulty">
            <div class="btn-group btn-group-toggle" data-toggle="buttons">
                <label class="btn btn-primary active"><input type="radio" name="difficulty" value="1" checked> Самый лёгкий</label>
                <label class="btn btn-info"><input type="radio" name="difficulty" value="2"> Лёгкий</label>
                <label class="btn btn-warning"><input type="radio" name="difficulty" value="3"> Средний</label>
                <label class="btn btn-danger"><input type="radio" name="difficulty" value="4"> Сложный</label>
                <label class="btn btn-dark"><input type="radio" name="difficulty" value="5"> Самый сложный</label>
            </div>
        </div>
        <div class="board mx-auto">
            {% for i in range(9) %}
            <div class="cell" id="{{ i }}">{{ session['board'][i] }}</div>
            {% endfor %}
        </div>
        <button class="btn btn-secondary button" onclick="resetGame()">Начать заново</button>
    </div>
    <!-- Модальное окно для результата игры -->
    <div class="modal fade" id="resultModal" tabindex="-1" role="dialog" aria-labelledby="resultModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="resultModalLabel">Игра окончена</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Закрыть">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body" id="resultMessage"></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Закрыть</button>
                    <button type="button" class="btn btn-primary" onclick="resetGame()">Начать заново</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
