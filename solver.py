import chess
import fen_generator
import minimax
import time

# Use alpha-beta pruning?
ALPHABETA = True
# Hash complete board scores?
HASHING = True
# Use zero evaluation?
ZERO = True
# Sort child states based on previous evals?
SORTING = False
# Do iterative deepening to obtain better hints?
DEEPENING = False

# Start the time and generate the puzzle.
time_start = time.process_time()
generator = fen_generator.FenGenerator()
fen = generator.get_board(0)
board = chess.Board(fen)
print(board, '\n')
# Initialize minimax.
mm = minimax.Minimax(ALPHABETA, HASHING, ZERO, SORTING)
# Play at most 5 turns.
for turn in range(5):
    # Do iterative deepening if needed.
    if DEEPENING:
        for depth in range(5 - turn):
            mm_info = mm.minimax(board, depth, mm.term_scores['0-1'],
                                 mm.term_scores['1-0'], False)
    # Find the best move.
    mm_info = mm.minimax(board, 5 - turn, mm.term_scores['0-1'],
                         mm.term_scores['1-0'], True)
    # Execute the move and print the new board state.
    print(board.san(mm_info.move), "(", mm_info.value, ")")
    board.push(mm_info.move)
    print(board, '\n')
    # Detect end of the game.
    if board.is_game_over():
        print('Game over: ', board.result())
        break
# Print statistics.
print(mm.get_stats())
time_end = time.process_time()
print("Time: {0:.2f}s".format(time_end - time_start))

'''
EVAL:

alphabeta hashing zero sorting deepening
    RESULT states_explored cutoffs_made time

0 0 0 0 0
    WIN 58k 0 56s
1 0 0 0 0
    WIN 30k 568 32s
1 1 0 0 0
    WIN 25k 493 18s
1 1 1 0 0
    WIN 14k 450 7s
1 1 1 1 0
    WIN 14k 450 26s
1 1 1 1 1
    WIN 15k 912 25s
'''