import numpy as np
import random
from model import WordleSolver
from config import * 
from wordle import result as get_scores,game
from trainer import run_training_loop, get_top_letters
from data_loader import *
import sys
import time

letter_to_int = {letter: i for i, letter in enumerate(alphabet)}

def game_state(current_answer_str, guesses):

    positional_state = np.zeros((26, 5))
    
    target_letters = list(current_answer_str)
    
    for guess in guesses:
        guess_letters = list(guess)
        scores = get_scores(guess_letters, target_letters)
        
        for i, (letter, score) in enumerate(zip(guess_letters, scores)):
            idx = letter_to_int.get(letter, -1)
            if idx != -1:

                if score > positional_state[idx][i]:
                    positional_state[idx][i] = score
                    
    return positional_state.flatten()

def run_benchmark(solver, num_games=100):
    total_turns = 0
    wins = 0
    
    random.seed(42)

    test_words = random.sample(solver.answer_list, num_games)
    
    for target in test_words:
        target_idx = solver.answer_to_index[target]
        solver.reset()
        
        for turn in range(1, 7):
            guess = solver.get_guess(turn)
            
            guess_idx = solver.word_to_index[guess]
            pattern_code = solver.words_matrix[guess_idx, target_idx]
            
            if pattern_code == 242: 
                wins += 1
                total_turns += turn
                break
            
            solver.update_internal(guess_idx, pattern_code)
        else:
            total_turns += 7 

    avg_guesses = total_turns / num_games
    win_percentage = (wins / num_games) * 100
    return avg_guesses, win_percentage

def reset_ai(solver):
    smallest_average = 5.0
    solver.weights = np.zeros((130,1), dtype=np.float64)
    solver.pair_weights = np.zeros((676,1),dtype=np.float64)
    for answer in solver.answer_list:
        for index,letter in enumerate(answer):
            idx = ord(letter) -97
            solver.weights[idx * 5 + index] += 0.01
    start = time.time()
    print(f"Beginning training on new gen | LR: {LEARNING_RATE}")
    total_turns = 0
    wins = 0
    for i in range(NUM_SAMPLES):
        current_lr = LEARNING_RATE * (1 - (i/NUM_SAMPLES) * 0.9)
        solver.lr = current_lr
        target_word = random.choice(answer_list)
        turns = solver.train_one_game(target_word)
        
        total_turns += min(turns, 7)
        if turns <=6: wins +=1

        if (i+1) % 200 == 0 or (i + 1) == NUM_SAMPLES:


            letter_totals = {}
            for j in range(26):
                char = chr(97 + j)
                total = np.sum(solver.weights[j*5 : (j+1)*5])
                letter_totals[char] = total
            percentage = ((i+1)/NUM_SAMPLES) * 100
            winrate = (wins/(i+1)) *100
            average =  (total_turns / (i + 1))
            filled_bar= int(50 * percentage/100)
            bar = '█' * filled_bar + '-' * (50 - filled_bar)
            sys.stdout.write(f"\r{bar}{percentage:.2f}% | WR: {winrate:.2f}% | Avg: {average:.2f} | TOP: {get_top_letters(solver.weights)}")    
            sys.stdout.flush()
            solver.winrate = winrate
            solver.average = average
            
            if average < smallest_average:
                smallest_average = average

    print(f"\nRun time: {time.time() - start} seconds")
    print(f"\n{smallest_average}")
    solver.save_weights()
    return solver 
if __name__ == "__main__":
    print("""select an option
          1)benchmark
          2)train
          3)see play
          4)new gen""")
    option = int(input())
    match option:
        case 1:
            solver = WordleSolver()
            print("Testing AI before training")
            old_avg, old_win = run_benchmark(solver)
            print(f"Before training: Avg Guesses: {old_avg:.2f}, Win Rate: {old_win}%")
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
    
            print(f"\nTraining completed in {total_time:.2f} seconds")
            new_avg, new_win = run_benchmark(solver)
            print(f"After training:  Avg Guesses: {new_avg:.2f}, Win Rate: {new_win}%")
            print(f"Improvement: {old_avg - new_avg:.2f} fewer guesses per game!")
            np.save("wordle_weights.npy",solver.weights)
        case 2:
            solver = WordleSolver() 
            run_training_loop()
            np.save("wordle_weights.npy", solver.weights)
            print("Training Complete")
        case 3:
            solver = WordleSolver()
            game(solver)
        case 4:
            reset_ai()