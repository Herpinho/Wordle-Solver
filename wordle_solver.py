import numpy as np
import random
from model import WordleSolver
from config import * 
from wordle import result as get_scores,print_color_coded_words,game
from data_loader import *
import sys
import time

char_to_int = {char: i for i, char in enumerate(alphabet)}

def game_state(current_answer_str, guesses):

    positional_state = np.zeros((26, 5))
    
    target_chars = list(current_answer_str)
    
    for guess in guesses:
        guess_chars = list(guess)
        scores = get_scores(guess_chars, target_chars)
        
        for i, (char, score) in enumerate(zip(guess_chars, scores)):
            idx = char_to_int.get(char, -1)
            if idx != -1:

                if score > positional_state[idx][i]:
                    positional_state[idx][i] = score
                    
    return positional_state.flatten()
def generate_training():
    inputs = []
    outputs = []

    print(f"Generating {NUM_SAMPLES} samples:")

    for i in range (NUM_SAMPLES):
        
        target_word = random.choice(answer_list)
        target_idx = answer_list.index(target_word)

        random_guess = random.choice(word_list)

        state_vector = game_state(target_word, [random_guess])

        inputs.append(state_vector)
        outputs.append(target_idx)
        percentage = (i+1)/NUM_SAMPLES
        filled_bar = int(20 * (percentage))
        bar = '█' * filled_bar + '-' * (20 - filled_bar)
        sys.stdout.write(f'\r{bar} {int(percentage*100)}% ({i+1}/{NUM_SAMPLES})')
        sys.stdout.flush()
    return np.array(inputs), np.array(outputs)

def run_benchmark(solver, num_games=100):
    total_turns = 0
    wins = 0
    
    random.seed(42)

    test_words = random.sample(solver.answer_list, num_games)
    
    for target in test_words:
        target_idx = solver.ans_to_idx[target]
        solver.reset()
        
        for turn in range(1, 7):
            guess = solver.get_guess(turn)
            
            guess_idx = solver.word_to_idx[guess]
            pattern_code = solver.pattern_matrix[guess_idx, target_idx]
            
            if pattern_code == 242: 
                wins += 1
                total_turns += turn
                break
            
            solver._update_internal(guess_idx, pattern_code)
        else:
            total_turns += 7 

    avg_guesses = total_turns / num_games
    win_percentage = (wins / num_games) * 100
    return avg_guesses, win_percentage
if __name__ == "__main__":
    print("""select an option
          1)benchmark
          2)train
          3)see play""")
    option = int(input())
    match option:
        case 1:
            solver = WordleSolver(26)
            print("Checking baseline performance...")
            old_avg, old_win = run_benchmark(solver)
            print(f"BEFORE: Avg Guesses: {old_avg:.2f}, Win Rate: {old_win}%")
            start_time = time.time()
            for i in range(NUM_SAMPLES):
                target_word = random.choice(answer_list)
                
                result_turn = solver.train_one_game(target_word)
                
                percentage = (i+1)/NUM_SAMPLES
                filled_bar = int(20 * (percentage))
                bar = '█' * filled_bar + '-' * (20 - filled_bar)
                sys.stdout.write(f'\r{bar} {int(percentage*100)}% ({i+1}/{NUM_SAMPLES})')
                sys.stdout.flush()
            end_time = time.time()
            total_time = end_time - start_time
    
            print(f"\nTraining completed in {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
            print("\nChecking post-training performance...")
            new_avg, new_win = run_benchmark(solver)
            print(f"AFTER:  Avg Guesses: {new_avg:.2f}, Win Rate: {new_win}%")
            print(f"Improvement: {old_avg - new_avg:.2f} fewer guesses per game!")
            np.save("wordle_weights.npy",solver.weights)
        case 2:
            solver = WordleSolver(26) 
            print(f"Starting Whole Game Training for {NUM_SAMPLES} games...")
            for i in range(NUM_SAMPLES):
                target_word = random.choice(answer_list)
                
                result_turn = solver.train_one_game(target_word)
                
                percentage = (i+1)/NUM_SAMPLES
                filled_bar = int(20 * (percentage))
                bar = '█' * filled_bar + '-' * (20 - filled_bar)
                sys.stdout.write(f'\r{bar} {int(percentage*100)}% ({i+1}/{NUM_SAMPLES})')
                sys.stdout.flush()
            np.save("wordle_weights.npy", solver.weights)
            print("Training Complete. Weights saved.")
        case 3:
            solver = WordleSolver(26)
            game(solver)