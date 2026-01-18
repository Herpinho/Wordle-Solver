import numpy as np
from config import *
from data_loader import *

word_to_index = {w: i for i, w in enumerate(word_list)}
answer_to_index = {w: i for i, w in enumerate(answer_list)}

class WordleSolver:
    def __init__(self):
        self.vocab_size = 26
        self.winrate = None
        self.average = None
        self.lr = LEARNING_RATE
        self.word_to_index = word_to_index
        self.answer_to_index = answer_to_index
        try:
            self.words_matrix = np.load(WORDS_MATRIX)
        except:
            self.words_matrix = np.zeros(())
        self.answer_list = answer_list
        self.word_list = word_list
        try:
            self.weights = np.load(WORDLE_WEIGHTS).astype(np.float64)
        except:
            self.weights = np.zeros((130, 1), dtype=np.float64)
        
        for answer in self.answer_list:
            for index, letter in enumerate(answer):
                idx = ord(letter) - 97
                weight_index = [idx * 5 + index]
                self.weights[weight_index] += 0.01
        
        try:
            self.pair_weights = np.load(PAIR_WEIGHTS).astype(np.float64)
        except:
            self.pair_weights = np.zeros((676, 1), dtype=np.float64)
            
        self.possible_guesses = np.ones(len(answer_list), dtype=bool)
        self.guessed_words = set()
        words_int = np.array([[ord(letter) - 97 for letter in word] for word in word_list], dtype=np.int8)
        self.weight_indices = (words_int * 5) + np.arange(5, dtype=np.int8)
        self.unique_factors = np.array([len(set(w)) / 5.0 for w in word_list]).reshape(-1, 1)
        self.ans_indices_in_full_list = np.array([word_to_index[answer] for answer in answer_list])
        self.pairs_indices = np.zeros((len(word_list), 4), dtype=int)

    def reset(self):
        self.possible_guesses[:] = True
        self.guessed_words.clear()

    def update_internal(self, guess_idx, pattern_code):
        matches = (self.words_matrix[guess_idx, :] == pattern_code)
        self.possible_guesses &= matches

    def update(self, last_guess, points):
        self.guessed_words.add(last_guess)     
        if last_guess in self.word_to_index:
            guess_idx = self.word_to_index[last_guess]           
            converted_points = []
            for p in points:
                if p == 3: converted_points.append(2)
                elif p == 2: converted_points.append(1)
                else: converted_points.append(0) 
            pattern_code = sum(p * (3**index) for index, p in enumerate(converted_points))
            self.update_internal(guess_idx, pattern_code)

    def find_best_filler(self, remaining_words):
        diff_letters = set()
        for word in remaining_words:
            for letter in word:
                diff_letters.add(letter)
        best_word = None
        max_score = -1
        for word in self.word_list:
            score = len(set(word) & diff_letters)
            if score > max_score:
                max_score = score
                best_word = word
        return best_word if max_score > -1 else None

    def get_guess(self, turn):
        w_flat = self.weights.ravel()[:130]
        
        possible_indices = np.where(self.possible_guesses)[0]
        count = len(possible_indices)
        if count == 0: return None
        if count == 1: return self.answer_list[possible_indices[0]]
        remaining_words = [self.answer_list[i] for i in possible_indices]
        if turn <= 3 and count > 50:
            endings = [w[3:] for w in remaining_words]
            if len(set(endings)) == 1: 
                filler = self.find_best_filler(remaining_words)
                if filler:
                    return filler 
            penalty_multiplier = np.ones(130, dtype=np.float32)
            used_chars = set("".join(self.guessed_words))
            char_indices = np.array([ord(c) - 97 for c in used_chars])
            
            if char_indices.size > 0:
                penalty_indices = (char_indices[:, None] * 5 + np.arange(5)).ravel()
                penalty_multiplier[penalty_indices] = 0.2

            w_penalized = w_flat * penalty_multiplier

            explore_scores = np.sum(w_penalized[self.weight_indices % 130], axis=1).reshape(-1, 1)
            explore_scores *= self.unique_factors
            
            for word in self.guessed_words:
                if word in self.word_to_index:
                    idx = self.word_to_index[word]
                    explore_scores[idx] = -np.inf

            return self.word_list[np.argmax(explore_scores)]

        return self.get_weighted_guess(possible_indices)

    def update_weights(self, guess, reduction_score, won, turn):
        current_reward = -10.0
        current_reward += np.log2(reduction_score + 1 ) * 40
    
        match turn:
                case 1: current_reward += 100
                case 2: current_reward += 500
                case 3: current_reward += 600
                case 4: current_reward += 200
                case 5: current_reward += -100
                case 6: current_reward -= 300
                case _: current_reward -= 500


        final_reward = current_reward * self.lr
        if guess in self.word_to_index:
            guess_int = np.array([ord(c) - 97 for c in guess])
            weight_indices = guess_int * 5 + np.arange(5)
            self.weights.ravel()[weight_indices] += final_reward
            
        indices = [ord(c) - 97 for c in guess]
        pair_indices = []
        for l in range(4):
            pair_indices.append(indices[l] * 26 + indices[l+1])
        self.pair_weights.ravel()[pair_indices] += final_reward

    def get_weighted_guess(self, possible_indices):
        full_list_indices = self.ans_indices_in_full_list[possible_indices]
        current_weight_indices = self.weight_indices[full_list_indices]
        scores = np.sum(self.weights.ravel()[current_weight_indices], axis=1)
        best_local_idx = np.argmax(scores)
        best_global_idx = possible_indices[best_local_idx]
        return self.answer_list[best_global_idx]

    def train_one_game(self, target):
        target_str = "".join(target) if isinstance(target, list) else target
        target_idx = self.answer_to_index[target_str]
        self.reset()
        game_log = []
        for turn in range(1, 7):
            num_possible_before = np.sum(self.possible_guesses)
            guess = self.get_guess(turn)
            if not guess:
                break
            game_log.append((guess, num_possible_before))
            self.guessed_words.add(guess)
            guess_idx = self.word_to_index[guess]
            pattern_code = self.words_matrix[guess_idx, target_idx]

            self.update_internal(guess_idx, pattern_code)
            num_possible_after = np.sum(self.possible_guesses)
            
            won = (pattern_code == 242)
            self.update_weights(guess, num_possible_before - num_possible_after, won, turn)
            
            if won:
                return turn
        #print(f"\n[!] LOSS DETECTED")
        #print(f"Target Word: {target_str}")
        #for i, (g, count) in enumerate(game_log):
         #   print(f"  Turn {i+1}: {g} (Possible answers before: {count})")
        #print("-" * 20)      
        return 7


    def save_weights(self):
        np.save(WORDLE_WEIGHTS, self.weights)
        np.save(PAIR_WEIGHTS, self.pair_weights)