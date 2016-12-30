import chess
import collections


class Minimax:

    # Scores for terminal states.
    term_scores = {'1-0': 1000, '0-1': -1000, '1/2-1/2': 0}
    # Piece values, kings are always on the board so their value is arbitrary.
    piece_score = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100,
                   'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -100}
    # Score for each possible move (<=250 estimate).
    MOBILITY_SCORE = 0.1

    # (best move, board value) tuple.
    MmInfo = collections.namedtuple('MmInfo', ['move', 'value'])
    # Mapping board FENs to complete scores and best moves.
    board_vals = dict()
    # Mapping board FENs to incomplete scores used as sorting hints.
    sorting_hints = dict()

    # Initialize the minimax object.
    def __init__(self, alphabeta, hashing, zero, sorting):
        self.iters = 0
        self.cutoffs = 0
        self.alphabeta = alphabeta
        self.hashing = hashing
        self.zero = zero
        self.sorting = sorting

    # Evaluate a terminal state.
    def _eval_game_over(self, board):
        if board.result() == '1-0':
                return self.term_scores[board.result()] - board.fullmove_number
        elif board.result() == '0-1':
            return self.term_scores[board.result()] + board.fullmove_number
        elif board.result() == '1/2-1/2':
            return self.term_scores[board.result()]  # stalemate
        raise Exception('Unknown board result.')

    # Evaluate a state.
    def _eval(self, board):
        # Check if we're in a terminal state.
        if board.is_game_over():
            return self._eval_game_over(board)
        # Score the board.
        score = 0
        # Score individual pieces.
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                score += self.piece_score[piece.symbol()]
        # Score possible moves for white.
        score += self.MOBILITY_SCORE * len(board.legal_moves)
        # Score possible moves for black.
        board.push(chess.Move.null())
        score -= self.MOBILITY_SCORE * len(board.legal_moves)
        board.pop()
        # Return the score.
        return score

    # Zero-evaluate a state: only terminal states or zero.
    def _zero_eval(self, board):
        if board.is_game_over():
            return self._eval_game_over(board)
        else:
            return 0

    # Get estimated score for the board after a move is executed.
    def _test(self, board, move):
        board.push(move)
        if self.hashing and board.fen() in self.board_vals:
            ret = self.board_vals[board.fen()].value
        elif board.fen() in self.sorting_hints:
            ret = self.sorting_hints[board.fen()]
        elif self.zero:
            ret = self.sorting_hints[board.fen()] = self._zero_eval(board)
        else:
            ret = self.sorting_hints[board.fen()] = self._eval(board)
        board.pop()
        return ret

    # Minimax algorithm.
    # board -> game state to evaluate
    # depth -> remaining depth to explore
    # alpha(min) -> lower bound, + player already knows better
    # beta(max) -> upper bound, - player already knows worse
    # full -> we're doing a full search (5 levels)
    # Returns (best_move, value) tuple.
    def minimax(self, board, depth, alpha, beta, full):
        self.iters += 1
        # Check if the info is already saved.
        if self.hashing and board.fen() in self.board_vals:
            return self.board_vals[board.fen()]

        # If it's a terminal position or max depth do an eval.
        if board.is_game_over() or depth == 0:
            if self.zero:
                val = self.MmInfo(chess.Move.null(), self._zero_eval(board))
            else:
                val = self.MmInfo(chess.Move.null(), self._eval(board))
            if self.sorting:
                self.sorting_hints[board.fen()] = val.value
            if full:
                self.board_vals[board.fen()] = val
            return val

        # Prepare moves.
        if self.sorting:
            moves = list(board.legal_moves)
        else:
            moves = board.legal_moves

        # WHITE (maximizing player) turn.
        if board.turn == chess.WHITE:
            # Initialize the info.
            mm_info = self.MmInfo(chess.Move.null(), self.term_scores['0-1'])
            # Optionally sort the possible moves.
            if self.sorting:
                moves.sort(key=lambda move: self._test(board, move),
                           reverse=True)
            # Traverse all possible moves.
            for move in moves:
                # Score a move and update the best solution if needed.
                board.push(move)
                child_mm_info = self.minimax(board, depth - 1,
                                             mm_info.value, beta, full)
                if child_mm_info.value >= mm_info.value:
                    mm_info = self.MmInfo(move, child_mm_info.value)
                board.pop()
                # Do a beta cutoff.
                if self.alphabeta and mm_info.value >= beta:
                    self.cutoffs += 1
                    break
        else:  # BLACK (minimizing player) turn.
            # Initialize the info.
            mm_info = self.MmInfo(chess.Move.null(), self.term_scores['1-0'])
            # Optionally sort the possible moves.
            if self.sorting:
                moves.sort(key=lambda move: self._test(board, move))
            # Traverse all possible moves.
            for move in moves:
                # Score a move and update the best solution if needed.
                board.push(move)
                child_mm_info = self.minimax(board, depth - 1,
                                             alpha, mm_info.value, full)
                if child_mm_info.value <= mm_info.value:
                    mm_info = self.MmInfo(move, child_mm_info.value)
                board.pop()
                # Do an alpha cutoff.
                if self.alphabeta and mm_info.value <= alpha:
                    self.cutoffs += 1
                    break
        # Return the score.
        if self.sorting:
            self.sorting_hints[board.fen()] = mm_info.value
        if full:
            self.board_vals[board.fen()] = mm_info
        return mm_info

    # Get a string with stats.
    def get_stats(self):
        return "Iters: " + str(self.iters) + " Cutoffs: " + str(self.cutoffs)
