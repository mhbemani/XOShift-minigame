from typing import List, Optional, Tuple
from copy import deepcopy
from agent_utils import get_all_valid_moves

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    valid_moves = get_all_valid_moves(board, player_symbol)
    if not valid_moves:
        return 0, 0, 0, 0

    opponent_symbol = 'O' if player_symbol == 'X' else 'X'

    def evaluate_board(temp_board: List[List[Optional[str]]], symbol: str, is_player: bool) -> int:
        score = 0
        size = len(temp_board)
        # Check rows
        for r in range(size):
            count = sum(1 for c in range(size) if temp_board[r][c] == symbol)
            score += count * (10 if is_player else -10)
            if is_player and count == size:
                score += 1000
            elif not is_player:
                if count == size - 1:
                    score -= 900
                elif count == size - 2:
                    score -= 100
                elif size >= 4 and count == size - 3:
                    score -= 50
                elif size >= 5 and count == size - 4:
                    score -= 20
        # Check columns
        for c in range(size):
            count = sum(1 for r in range(size) if temp_board[r][c] == symbol)
            score += count * (10 if is_player else -10)
            if is_player and count == size:
                score += 1000
            elif not is_player:
                if count == size - 1:
                    score -= 900
                elif count == size - 2:
                    score -= 100
                elif size >= 4 and count == size - 3:
                    score -= 50
                elif size >= 5 and count == size - 4:
                    score -= 20
        # Check main diagonal
        count = sum(1 for i in range(size) if temp_board[i][i] == symbol)
        score += count * (10 if is_player else -10)
        if is_player and count == size:
            score += 1000
        elif not is_player:
            if count == size - 1:
                score -= 900
            elif count == size - 2:
                score -= 100
            elif size >= 4 and count == size - 3:
                score -= 50
            elif size >= 5 and count == size - 4:
                score -= 20
        # Check anti-diagonal
        count = sum(1 for i in range(size) if temp_board[i][size-1-i] == symbol)
        score += count * (10 if is_player else -10)
        if is_player and count == size:
            score += 1000
        elif not is_player:
            if count == size - 1:
                score -= 900
            elif count == size - 2:
                score -= 100
            elif size >= 4 and count == size - 3:
                score -= 50
            elif size >= 5 and count == size - 4:
                score -= 20
        return score

    def apply_move(temp_board: List[List[Optional[str]]], move: Tuple[int, int, int, int]) -> List[List[Optional[str]]]:
        temp_board = deepcopy(temp_board)
        src_r, src_c, tgt_r, tgt_c = move
        if src_r == tgt_r:
            step = 1 if tgt_c > src_c else -1
            for c in range(src_c, tgt_c, step):
                temp_board[src_r][c] = temp_board[src_r][c + step]
        else:
            step = 1 if tgt_r > src_r else -1
            for r in range(src_r, tgt_r, step):
                temp_board[r][src_c] = temp_board[r + step][src_c]
        temp_board[tgt_r][tgt_c] = player_symbol
        return temp_board

    best_move = valid_moves[0]
    best_score = -float('inf')
    for move in valid_moves:
        temp_board = apply_move(board, move)
        score = evaluate_board(temp_board, player_symbol, True) + evaluate_board(temp_board, opponent_symbol, False)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move