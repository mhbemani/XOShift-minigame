from agent_utils import get_all_valid_moves
import copy
import time
import random
import os, json
from typing import List, Optional, Tuple

# Configurable parameters
MAX_DEPTH = 4
TIME_LIMIT = 1.9
DEPTH_DISCOUNT = 0.4
BEAM_WIDTH = 4
CHECK_BACK_CAPACITY = 8

# Scoring parameters
SCORE_2 = 10
SCORE_3 = 100
SCORE_4 = 1000
WIN_SCORE = 10000

PAST_MOVES_FILE = "past_moves.json"

class TimeoutException(Exception):
    pass

def apply_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], player_symbol: str) -> None:
    sr, sc, tr, tc = move
    if sr == tr:  # Horizontal move
        direction = 1 if tc > sc else -1
        for col in range(sc, tc, direction):
            board[sr][col] = board[sr][col + direction]
    else:  # Vertical move
        direction = 1 if tr > sr else -1
        for row in range(sr, tr, direction):
            board[row][sc] = board[row + direction][sc]
    board[tr][tc] = player_symbol

def check_winner(board: List[List[Optional[str]]], player_symbol: str) -> bool:
    size = len(board)
    for i in range(size):
        if all(cell == player_symbol for cell in board[i]):
            return True
        if all(board[j][i] == player_symbol for j in range(size)):
            return True
    if all(board[i][i] == player_symbol for i in range(size)):
        return True
    if all(board[i][size-1-i] == player_symbol for i in range(size)):
        return True
    return False

def evaluate_line(line, player, opponent, size):
    p_count = line.count(player)
    o_count = line.count(opponent)
    if p_count == size: return WIN_SCORE
    if o_count == size: return -WIN_SCORE
    score = 0
    if p_count >= 2 :
        score += [0, 0, SCORE_2, SCORE_3, SCORE_4][min(p_count, 4)]
    if o_count >= 2 :
        score -= [0, 0, SCORE_2, SCORE_3, SCORE_4][min(o_count, 4)]
    return score

def evaluate_board(board: List[List[Optional[str]]], player_symbol: str) -> int:
    opponent = 'O' if player_symbol == 'X' else 'X'
    size = len(board)
    score = 0
    if check_winner(board, player_symbol): return WIN_SCORE
    if check_winner(board, opponent): return -WIN_SCORE
    for i in range(size):
        score += evaluate_line(board[i], player_symbol, opponent, size)
        score += evaluate_line([board[j][i] for j in range(size)], player_symbol, opponent, size)
    score += evaluate_line([board[i][i] for i in range(size)], player_symbol, opponent, size)
    score += evaluate_line([board[i][size-1-i] for i in range(size)], player_symbol, opponent, size)
    return score

def minimax(board, depth, is_max, player_symbol, alpha, beta, start_time, current_depth):
    if time.time() - start_time > TIME_LIMIT:
        raise TimeoutException()

    opponent = 'O' if player_symbol == 'X' else 'X'
    if depth == 0 or check_winner(board, player_symbol) or check_winner(board, opponent):
        return evaluate_board(board, player_symbol) * (DEPTH_DISCOUNT ** current_depth)

    moves = get_all_valid_moves(board, player_symbol if is_max else opponent)

    # === Beam search part: score and keep top BEAM_WIDTH ===
    scored_moves = []
    for move in moves:
        tmp_board = copy.deepcopy(board)
        apply_move(tmp_board, move, player_symbol if is_max else opponent)
        score = evaluate_board(tmp_board, player_symbol)
        scored_moves.append((score, move))
    # Sort moves: max wants high scores first, min wants low scores first
    reverse = is_max
    scored_moves.sort(reverse=reverse, key=lambda x: x[0])
    # Keep only best BEAM_WIDTH moves
    moves = [m for (_, m) in scored_moves[:BEAM_WIDTH]]

    best_val = float('-inf') if is_max else float('inf')

    for move in moves:
        new_board = copy.deepcopy(board)
        apply_move(new_board, move, player_symbol if is_max else opponent)
        val = minimax(new_board, depth-1, not is_max, player_symbol, alpha, beta, start_time, current_depth+1)
        if is_max:
            best_val = max(best_val, val)
            alpha = max(alpha, val)
        else:
            best_val = min(best_val, val)
            beta = min(beta, val)
        # ///////////////      p r u n n i n g    h a s    b e e n    r e m o v e d      ///////////////
         # if beta <= alpha:
        #     break
        # ///////////////      p r u n n i n g    h a s    b e e n    r e m o v e d      ///////////////
        if time.time() - start_time > TIME_LIMIT:
            raise TimeoutException()

    return best_val


def board_to_hash(board):
    return ''.join([''.join(['_' if cell is None else cell for cell in row]) for row in board])

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    # global past_moves
    # CHECK_BACK_CAPACITY = 5

    start_time = time.time()
    best_move: Tuple[int, int, int, int] = (0, 0, 0, 0)
    best_score = float('-inf')
    valid_moves = get_all_valid_moves(board, player_symbol)
    size = len(board)
    if not valid_moves:
        return (0, 0, 0, 0)
    if len(valid_moves) == 1:
        return valid_moves[0]

    global MAX_DEPTH, TIME_LIMIT
    # if size == 5:
    #     MAX_DEPTH = min(MAX_DEPTH, 3)
    #     TIME_LIMIT = 1.8
    # elif size == 4:
    #     MAX_DEPTH = min(MAX_DEPTH, 4)
    #     TIME_LIMIT = 1.9
    # else:
    #     MAX_DEPTH = min(MAX_DEPTH, 5)
    #     TIME_LIMIT = 2.0

    if size == 3:
        WIN_SCORE = SCORE_3
    elif size == 4:
        WIN_SCORE = SCORE_4

    try:
        candidate_moves = valid_moves
        # print("moves currentlly are as below befor running the functions:")
        # for i in candidate_moves:
        #     print("move: ", i)
        # # candidate_moves_backup = candidate_moves
        for depth in range(1, MAX_DEPTH + 1):
            scored_moves = []
            current_best_move = None
            current_best_score = float('-inf')
            for move in candidate_moves:
                if time.time() - start_time > TIME_LIMIT:
                    raise TimeoutException()
                new_board = copy.deepcopy(board)
                apply_move(new_board, move, player_symbol)
                if depth == 1:
                    score = evaluate_board(new_board, player_symbol)
                else:
                    score = minimax(new_board, depth-1, False, player_symbol,
                                    float('-inf'), float('inf'), start_time, 1)
                scored_moves.append((score, move))
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move
            if current_best_move is not None:
                best_move = current_best_move
                best_score = current_best_score
            # Beam search: keep top BEAM_WIDTH moves
            scored_moves.sort(reverse=True, key=lambda x: x[0])
            candidate_moves = [m for (_, m) in scored_moves[:BEAM_WIDTH]]

            # print("moves currentlly are as below:")
            # for i in candidate_moves:
            #     print("move: ", i)


        # /////////////////////           m y   c o d e             ///////////////////////
        try:
            if os.path.exists(PAST_MOVES_FILE):
                with open(PAST_MOVES_FILE, "r") as f:
                    try:
                        past_moves = json.load(f)
                    except json.JSONDecodeError:
                        past_moves = []
            else:
                past_moves = []
                with open(PAST_MOVES_FILE, "w") as f:
                    json.dump(past_moves, f)
        except (FileNotFoundError, json.JSONDecodeError):
            past_moves = []
        
        board_hash = ''.join([''.join(['_' if c is None else c for c in row]) for row in board])
        key = {"board": board_hash, "move": list(best_move)}
        flag = False
        
        if key in past_moves:
            
            for i in candidate_moves:
                
                other_key = {"board": board_hash, "move": list(i)}
                if other_key not in past_moves:
                    past_moves.append(other_key)
                    best_move = i
                    flag = True
                    break
                
            if not flag:
                for i in candidate_moves:
                    print("move: ", i)
                best_move = random.choice(candidate_moves)
                past_moves.append({"board": board_hash, "move": best_move})
        else:
            past_moves.append({"board": board_hash, "move": best_move})
        
        if len(past_moves) > CHECK_BACK_CAPACITY:
            past_moves.pop(0)

        with open(PAST_MOVES_FILE, "w") as f:
            json.dump(past_moves, f, indent=4)
        # /////////////////////           m y   c o d e             ///////////////////////
            
            
            


    except TimeoutException:
        pass
    return best_move if best_move else valid_moves[0]
