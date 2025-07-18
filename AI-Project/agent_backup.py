from agent_utils import get_all_valid_moves
import copy
import time
from typing import List, Optional, Tuple

# Configurable parameters - ADJUST THESE FOR PERFORMANCE
MAX_DEPTH = 3                    # Reduced from 4 for 5x5 boards
TIME_LIMIT = 1.8                 # Reduced from 2.0 to ensure we don't timeout
DEPTH_DISCOUNT = 0.7             # Increased from 0.5 to prioritize earlier depths

# Scoring parameters
SCORE_2 = 2
SCORE_3 = 50
SCORE_4 = 1000
WIN_SCORE = 10000

class TimeoutException(Exception):
    pass

def apply_move(board: List[List[Optional[str]]], move: Tuple[int, int, int, int], player_symbol: str) -> None:
    # Optimized move application
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
    # Check rows and columns
    for i in range(size):
        if all(cell == player_symbol for cell in board[i]):
            return True
        if all(board[j][i] == player_symbol for j in range(size)):
            return True
    # Check diagonals
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
    if p_count >= 2 and o_count == 0:
        score += [0, 0, SCORE_2, SCORE_3, SCORE_4][min(p_count, 4)]
    if o_count >= 2 and p_count == 0:
        score -= [0, 0, SCORE_2, SCORE_3, SCORE_4][min(o_count, 4)]
    return score

def evaluate_board(board: List[List[Optional[str]]], player_symbol: str) -> int:
    opponent = 'O' if player_symbol == 'X' else 'X'
    size = len(board)
    score = 0

    # Immediate win/loss check
    if check_winner(board, player_symbol): return WIN_SCORE
    if check_winner(board, opponent): return -WIN_SCORE

    # Evaluate all lines
    for i in range(size):
        score += evaluate_line(board[i], player_symbol, opponent, size)  # Rows
        score += evaluate_line([board[j][i] for j in range(size)], player_symbol, opponent, size)  # Columns
    
    # Diagonals
    score += evaluate_line([board[i][i] for i in range(size)], player_symbol, opponent, size)
    score += evaluate_line([board[i][size-1-i] for i in range(size)], player_symbol, opponent, size)
    
    return score

def minimax(board, depth, is_max, player_symbol, alpha, beta, start_time, current_depth):
    if time.time() - start_time > TIME_LIMIT:
        raise TimeoutException()

    opponent = 'O' if player_symbol == 'X' else 'X'
    
    # Terminal node evaluation
    if depth == 0 or check_winner(board, player_symbol) or check_winner(board, opponent):
        return evaluate_board(board, player_symbol) * (DEPTH_DISCOUNT ** current_depth)

    moves = get_all_valid_moves(board, player_symbol if is_max else opponent)
    best_val = float('-inf') if is_max else float('inf')

    for move in moves:
        new_board = copy.deepcopy(board)
        apply_move(new_board, move, player_symbol if is_max else opponent)
        
        val = minimax(new_board, depth-1, not is_max, player_symbol, alpha, beta, start_time, current_depth+1)
        
        if is_max:
            if val > best_val:
                best_val = val
            alpha = max(alpha, val)
        else:
            if val < best_val:
                best_val = val
            beta = min(beta, val)
        
        if beta <= alpha:
            break
        
        # Early timeout check
        if time.time() - start_time > TIME_LIMIT:
            raise TimeoutException()

    return best_val

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    start_time = time.time()
    best_move = None
    best_score = float('-inf')
    valid_moves = get_all_valid_moves(board, player_symbol)
    size = len(board)
    
    if not valid_moves:
        return (0, 0, 0, 0)  # Should never happen
    
    # Immediate return if only one move
    if len(valid_moves) == 1:
        return valid_moves[0]

    # Adjust parameters based on board size
    global MAX_DEPTH, TIME_LIMIT
    if size == 5:
        MAX_DEPTH = min(MAX_DEPTH, 3)  # Lower depth for 5x5
        TIME_LIMIT = 1.8
    elif size == 4:
        MAX_DEPTH = min(MAX_DEPTH, 4)
        TIME_LIMIT = 1.9
    else:  # 3x3
        MAX_DEPTH = min(MAX_DEPTH, 5)
        TIME_LIMIT = 2.0

    try:
        for depth in range(1, MAX_DEPTH + 1):
            current_best_move = None
            current_best_score = float('-inf')
            
            for move in valid_moves:
                if time.time() - start_time > TIME_LIMIT:
                    raise TimeoutException()
                    
                new_board = copy.deepcopy(board)
                apply_move(new_board, move, player_symbol)
                
                if depth == 1:
                    score = evaluate_board(new_board, player_symbol)
                else:
                    score = minimax(new_board, depth-1, False, player_symbol, 
                                   float('-inf'), float('inf'), start_time, 1)
                
                if score > current_best_score or current_best_move is None:
                    current_best_score = score
                    current_best_move = move
            
            if current_best_move is not None:
                best_move = current_best_move
                best_score = current_best_score

    except TimeoutException:
        pass

    return best_move if best_move else valid_moves[0]  # Fallback