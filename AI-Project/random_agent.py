from typing import List, Optional, Tuple
import random
from agent_utils import get_all_valid_moves

def agent_move(board: List[List[Optional[str]]], player_symbol: str) -> Tuple[int, int, int, int]:
    valid_moves = get_all_valid_moves(board, player_symbol)
    if not valid_moves:
        return 0, 0, 0, 0
    
    # Randomly select a move from valid moves
    return random.choice(valid_moves)