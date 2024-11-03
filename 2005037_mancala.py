from typing import Tuple
import copy
import random
import pandas as pd


def print_board(board: dict, player_1: str = "P_1", player_2: str = "P_2") -> None:

    print(
        f"""
   {''.join(f'{(len(board["top"]) - num):3}' for num in range(len(board['top'])))}
+---+{'--+'*len(board['top'])}---+
|{player_1}|{'|'.join(f'{item:2}' for item in reversed(board['top']))}|   | <- PLAYER 1
|{board["top_score"]:3}+{'--+'*len(board['top'])}{board["bottom_score"]:3}|
|   |{'|'.join(f'{item:2}' for item in board['bottom'])}|{player_2}| PLAYER 2 ->
+---+{'--+'*len(board['bottom'])}---+
   {''.join(f'{(num+1):3}' for num in range(len(board['bottom'])))}
"""
    )
    return


def move_piece(board: dict, tile: int, turn: str) -> Tuple[dict]:
    # returns the board after the move,go_again,stones_captured

    pieces = board[turn][tile]
    board[turn][tile] = 0
    location = turn
    go_again = False
    stones_captured = 0

    #  Moving counter-clockwise
    while pieces > 0:
        go_again = False
        pieces -= 1
        tile += 1

        if tile < len(board[location]):
            board[location][tile] += 1
            continue

        if location == turn:
            board[f"{turn}_score"] += 1
            go_again = True
        else:
            pieces += 1

        location = "bottom" if location == "top" else "top"
        tile = -1

    inverse_location = "bottom" if location == "top" else "top"
    if (
        (location == turn)
        and (board[location][tile] == 1)
        and (board[inverse_location][len(board[inverse_location]) - 1 - tile] != 0)
    ):
        stones_captured = (
            1 + board[inverse_location][len(board[inverse_location]) - 1 - tile]
        )

        board[f"{turn}_score"] += stones_captured

        board[location][tile] = 0
        board[inverse_location][len(board[inverse_location]) - 1 - tile] = 0

   
    if (not any(board["top"])) or (not any(board["bottom"])):
        board["top_score"] += sum(board["top"])
        board["bottom_score"] += sum(board["bottom"])

        board["top"] = [0] * len(board["top"])
        board["bottom"] = [0] * len(board["bottom"])

        go_again = False

    board["go_again"] = go_again
    board["stones_captured"] = stones_captured

    return board


def is_viable_move(board: dict, tile: int, turn: str) -> bool:

    if tile >= len(board[turn]) or tile < 0:
        return False
    return bool(board[turn][tile])


def heuristic_1(board: dict, maximizing_player: str) -> int:
    """Naive heuristic based on the difference in storage stones."""
    ai_score = board[f"{maximizing_player}_score"]
    player_score = board[f"{'bottom' if maximizing_player == 'top' else 'top'}_score"]
    return ai_score - player_score


def heuristic_2(board: dict, maximizing_player: str) -> int:
    """Heuristic based on storage difference and stones on each side."""

    ai_score = board[f"{maximizing_player}_score"]
    opponent = "bottom" if maximizing_player == "top" else "top"
    opponent_score = board[f"{opponent}_score"]

    stones_on_ai_side = sum(board[maximizing_player])
    stones_on_opponent_side = sum(board[opponent])

    W1 = weights[0]
    W2 = weights[1]

    return (W1 * (ai_score - opponent_score)) + (
        W2 * (stones_on_ai_side - stones_on_opponent_side)
    )


def heuristic_3(board: dict, maximizing_player: str) -> int:
    """Heuristic considering storage difference, side control, and extra moves."""

    W1 = weights[0]
    W2 = weights[1]
    W3 = weights[2]

    ai_score = board[f"{maximizing_player}_score"]
    opponent = "bottom" if maximizing_player == "top" else "top"
    opponent_score = board[f"{opponent}_score"]

    stones_on_ai_side = sum(board[maximizing_player])
    stones_on_opponent_side = sum(board[opponent])

    # Extra points for earning an additional move
    extra_move_points = W3 if board["go_again"] else 0

    return (
        (W1 * (ai_score - opponent_score))
        + (W2 * (stones_on_ai_side - stones_on_opponent_side))
        + extra_move_points
    )


def heuristic_4(board: dict, maximizing_player: str) -> int:
    """Heuristic considering storage difference, side control, extra moves, and captures."""

    W1 = weights[0]
    W2 = weights[1]
    W3 = weights[2]
    W4 = weights[3]

    ai_score = board[f"{maximizing_player}_score"]
    opponent = "bottom" if maximizing_player == "top" else "top"
    opponent_score = board[f"{opponent}_score"]

    stones_on_ai_side = sum(board[maximizing_player])
    stones_on_opponent_side = sum(board[opponent])

    # Extra points for earning an additional move
    extra_move_points = W3 if board["go_again"] else 0

    # Captured stones score
    captured_points = W4 * board["stones_captured"]

    return (
        (W1 * (ai_score - opponent_score))
        + (W2 * (stones_on_ai_side - stones_on_opponent_side))
        + extra_move_points
        + captured_points
    )


def minimax_mancala(
    board: dict,
    ai_side: str,
    turn: str,
    depth: int,
    alpha: int,
    beta: int,
    heuristic_function: callable,
) -> Tuple[int, int]:

    AI = ai_side  # maximizing player
    PLAYER = "bottom" if AI == "top" else "top"  # minimizing player
    best_move = -1

    # Terminal case: game over or maximum depth reached
    if (not any(board["top"])) or (not any(board["bottom"])) or depth <= 0:

        # return board[f"{AI}_score"] - board[f"{PLAYER}_score"], best_move
        return heuristic_function(board, ai_side), best_move

    if AI == turn:
        # Maximizing player's turn (AI)
        best_score = float("-inf")

        possible_moves = [
            move for move in range(len(board[AI])) if is_viable_move(board, move, AI)
        ]

        for move in possible_moves:

            board_copy = copy.deepcopy(board)

            board_copy = move_piece(board_copy, move, turn)

            if board_copy["go_again"]:
                points, _ = minimax_mancala(
                    board_copy, AI, AI, depth, alpha, beta, heuristic_function
                )
            else:
                points, _ = minimax_mancala(
                    board_copy, AI, PLAYER, depth - 1, alpha, beta, heuristic_function
                )

            # The MAX part of minimax with alpha-beta pruning
            if points > best_score:
                best_move = move
                best_score = points

            # Updating alpha and check for pruning
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break  # Beta cutoff: pruning the remaining branches

    else:
        # Minimizing player's turn (Opponent)
        best_score = float("inf")

        possible_moves = [
            move
            for move in range(len(board[PLAYER]))
            if is_viable_move(board, move, PLAYER)
        ]

        for move in possible_moves:
            board_copy = copy.deepcopy(board)
            board_copy = move_piece(board_copy, move, turn)

            if board_copy["go_again"]:
                points, _ = minimax_mancala(
                    board_copy, AI, PLAYER, depth, alpha, beta, heuristic_function
                )
            else:
                points, _ = minimax_mancala(
                    board_copy, AI, AI, depth - 1, alpha, beta, heuristic_function
                )

            # The MIN part of minimax with alpha-beta pruning
            if points < best_score:
                best_move = move
                best_score = points

            # Updating beta and check for pruning
            beta = min(beta, best_score)
            if alpha >= beta:
                break  # Alpha cutoff: pruning the remaining branches

    return best_score, best_move


def play_game(
    PLAYER: str,
    MAX_DEPTH: int,
    PLAYER_heuristic: int,
    AI_heuristic: int
):

    # board Schema

    board = {
        "top": [4, 4, 4, 4, 4, 4],
        "bottom": [4, 4, 4, 4, 4, 4],
        "top_score": 0,
        "bottom_score": 0,
        "go_again": False,  # will the player get another turn?
        "stones_captured": 0,  # how many stones have been captured in the current move
    }

    turn = "top"

    # Some final inits before starting the game

    P1 = "h"+str(PLAYER_heuristic+1) if PLAYER == "top" else "h"+str(AI_heuristic+1)

    P2 = "h"+str(PLAYER_heuristic+1) if PLAYER == "bottom" else "h"+str(AI_heuristic+1)

    AI = "bottom" if PLAYER == "top" else "top"


    ai_printed_moves = []

    game = [P1,P2,MAX_DEPTH]

    for i in range(len(weights)):
        game.append(weights[i])

    # While the games not over
    while not ((not any(board["top"])) or (not any(board["bottom"]))):
        # Players move
        if turn == PLAYER:
            # Getting the players move
            alpha = float("-inf")
            beta = float("inf")

            _, suggested_move = minimax_mancala(
                board, AI, turn, MAX_DEPTH, alpha, beta, heuristics[PLAYER_heuristic]
            )

            # print(f"suggested move: {suggested_move+1}")

            # Updating the board
            # move = get_player_move(board, PLAYER)
            move = suggested_move

            board = move_piece(board, move, PLAYER)

            go_again = board["go_again"]

        # AI's move
        elif turn == AI:
            # Getting the AI's move with the Minimax function
            alpha = float("-inf")
            beta = float("inf")

            best_score, move = minimax_mancala(
                board, AI, turn, MAX_DEPTH, alpha, beta, heuristics[AI_heuristic]
            )

            ai_printed_moves.append(f"AI Moved : {move+1}")

            # Updating the board
            board = move_piece(board, move, AI)

            go_again = board["go_again"]

        # 4. If the last piece dropped is in your own Mancala, you take another turn.
        if not go_again:
            turn = "bottom" if turn == "top" else "top"

        if (turn == PLAYER) and ai_printed_moves:
            # [print(move) for move in ai_printed_moves]
            ai_printed_moves = []

        # print_board(board, P1, P2)
    
    game.append(board["top_score"])
    game.append(board["bottom_score"])

    # WIN / LOSS / DRAW
    if board[f"{PLAYER}_score"] > board[f"{AI}_score"]:
        
        result = "P1" if PLAYER=="top" else "P2"

    elif board[f"{PLAYER}_score"] < board[f"{AI}_score"]:
       
        result = "P1" if AI=="top" else "P2"
    else:
       
        result = "draw"

    game.append(result)

    print(f"game information: {game}")

    gameframe.loc[len(gameframe)] = game


heuristics = [heuristic_1,heuristic_2,heuristic_3,heuristic_4] #list of callable functions
weights = [0,0,0,0] #list of weights
turn = ["top","bottom"]
UPPER = 5
LOWER = 1
MAXIMUM_DEPTH = 6
MINIMUM_DEPTH = 3
gameframe = pd.DataFrame(columns=["P1","P2","depth","W1","W2","W3","W4","P1_score","P2_score","result"])

def generate_random_weights():

    for i in range(len(weights)):

        weights[i] = random.randint(LOWER,UPPER)


def main():

    N = 100

    for i in range(N):
        
        turn_index = random.randint(0,len(turn)-1)
        depth = random.randint(MINIMUM_DEPTH,MAXIMUM_DEPTH)
        generate_random_weights()
        p1_heuristic_index = random.randint(0,len(heuristics)-1)
        p2_heuristic_index = random.randint(0,len(heuristics)-1)
        play_game(turn[turn_index],depth,p1_heuristic_index,p2_heuristic_index)

    print(gameframe.head())
    gameframe.to_csv('analysis.csv',index=False)

if __name__ == "__main__":
    main()
