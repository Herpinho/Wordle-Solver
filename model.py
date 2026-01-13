import numpy as np
from config import *
from data_loader import *

pattern_matrix = np.load("pattern_matrix.npy")
word_to_idx = {w: i for i, w in enumerate(word_list)}
ans_to_idx = {w: i for i, w in enumerate(answer_list)}

class WordleSolver:
    def __init__(self, vocab_size):
        self.vocab_size = vocab_size
        self.lr = LEARNING_RATE
        
        self.word_to_idx = word_to_idx
        self.ans_to_idx = ans_to_idx
        self.pattern_matrix = pattern_matrix
        self.answer_list = answer_list
        self.word_list = word_list
        
        try:
            self.weights = np.load(WORDLE_WEIGHTS)
            if self.weights.shape != (130, 1):
                self.weights = np.zeros((130, 1))
        except:
            self.weights = np.zeros((130, 1))

        self.possible_mask = np.ones(len(answer_list), dtype=bool)
        self.guessed_words = set()
        

        words_int = np.array([[ord(c) - 97 for c in w] for w in word_list], dtype=np.int8)
        col_offsets = np.arange(5, dtype=np.int8)
        self.weight_indices = (words_int * 5) + col_offsets
        
        self.unique_factors = np.array([len(set(w)) / 5.0 for w in word_list]).reshape(-1, 1)
        self.ans_indices_in_full_list = np.array([word_to_idx[w] for w in answer_list])

    def reset(self):
        self.possible_mask[:] = True
        self.guessed_words.clear()

    def _update_internal(self, guess_idx, pattern_code):
        matches = (self.pattern_matrix[guess_idx, :] == pattern_code)
        self.possible_mask &= matches

    def update(self, last_guess, points):
        self.guessed_words.add(last_guess)
        
        if last_guess in self.word_to_idx:
            guess_idx = self.word_to_idx[last_guess]
            
            converted_points = []
            for p in points:
                if p == 3: converted_points.append(2)
                elif p == 2: converted_points.append(1)
                else: converted_points.append(0)
            
            pattern_code = sum(p * (3**i) for i, p in enumerate(converted_points))
            self._update_internal(guess_idx, pattern_code)

    def get_guess(self, turn):
        

        w_flat = self.weights.ravel()
        raw_scores = np.sum(w_flat[self.weight_indices], axis=1)
        base_scores = raw_scores * self.unique_factors.ravel()

        for word in self.guessed_words:
            if word in self.word_to_idx:
                idx = self.word_to_idx[word]
                base_scores[idx] = -np.inf

        possible_indices = np.where(self.possible_mask)[0]
        count = len(possible_indices)

        if count == 0: return None
        if count == 1: return self.answer_list[possible_indices[0]]

        
        
        
        if turn <= 2 and count > 40:
            penalty_multiplier = np.ones(130, dtype=np.float32)
            
            
            for prev_word in self.guessed_words:
                for char_code in [ord(c) - 97 for c in prev_word]:
                    for pos in range(5):
                        penalty_multiplier[char_code * 5 + pos] = 0.2

            w_penalized = w_flat * penalty_multiplier
            explore_scores = np.sum(w_penalized[self.weight_indices], axis=1)
            explore_scores *= self.unique_factors.ravel()
            
            for word in self.guessed_words:
                if word in self.word_to_idx:
                    idx = self.word_to_idx[word]
                    explore_scores[idx] = -np.inf

            best_idx = np.argmax(explore_scores)
            return self.word_list[best_idx]

        global_indices = self.ans_indices_in_full_list[possible_indices]
        
        if len(global_indices) == 0:
            return self.word_list[np.argmax(base_scores)]

        subset_argmax = np.argmax(base_scores[global_indices])
        return self.answer_list[possible_indices[subset_argmax]]

    def update_weights(self, guess, reduction_score, won, turn):

        if won:
            final_reward = 50.0 * (7 - turn) 
        else:
            final_reward = -0.5 * turn 
            
        final_reward *= self.lr

        if guess in self.word_to_idx:
            guess_int = np.array([ord(c) - 97 for c in guess])
            weight_indices = guess_int * 5 + np.arange(5)
            self.weights.ravel()[weight_indices] += final_reward

    def train_one_game(self, target):
        target_str = "".join(target) if isinstance(target, list) else target
        target_idx = self.ans_to_idx[target_str]
        self.reset()
        
        for turn in range(1, 7):
            num_possible_before = np.sum(self.possible_mask)
            
            guess = self.get_guess(turn)
            if not guess:
                break
            
            self.guessed_words.add(guess)
            
            guess_idx = self.word_to_idx[guess]
            pattern_code = self.pattern_matrix[guess_idx, target_idx]
            
            self._update_internal(guess_idx, pattern_code)
            
            num_possible_after = np.sum(self.possible_mask)
            
            won = (pattern_code == 242)
            
            self.update_weights(guess, num_possible_before - num_possible_after, won, turn)
            
            if won:
                return turn
                
        return 7

    def save_weights(self):
        np.save(WORDLE_WEIGHTS, self.weights)