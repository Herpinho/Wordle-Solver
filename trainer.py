from config import *
import random
import sys
import numpy as np
import time
from data_loader import *
from model import WordleSolver
model = WordleSolver()
def run_training_loop():
    total_reward = 0 
    total_turns = 0
    wins = 0
    initial_lr = LEARNING_RATE
    print(f"Began training (Learning Rate: {LEARNING_RATE}")
    for i in range(NUM_SAMPLES):
        current_lr = initial_lr * (1 - (i / NUM_SAMPLES) * 0.9) 
        model.lr = current_lr
        target_word = random.choice(answer_list)
        turns = model.train_one_game(target_word)       
        match turns:
            case 1: current_reward = 500
            case 2: current_reward = 300
            case 3: current_reward = 150
            case 4: current_reward = 40
            case 5: current_reward = 10
            case 6: current_reward = -20
            case _: current_reward = -100
        total_reward += current_reward
        total_turns += min(turns, 7)
        if turns <= 6: wins += 1
        if (i + 1) % 500 == 0 or (i + 1) == NUM_SAMPLES:
            avg_place = total_turns / (i + 1)
            win_rate = (wins / (i + 1)) * 100
            top_str = get_top_letters(model.weights)          
            percentage = (i + 1) / NUM_SAMPLES
            filled_bar = int(20 * percentage)
            bar = '█' * filled_bar + '-' * (20 - filled_bar)      
            sys.stdout.write(
                f'\r{bar} {int(percentage*100)}% | WR: {win_rate:.1f}% | Avg: {avg_place:.2f} | Top: [{top_str}]'
            )
            sys.stdout.flush()


def get_top_letters(weights):
    letter_totals = {}
    for i in range(26):
        letter = chr(97 + i)
        total = np.sum(weights[i*5 : (i+1)*5])
        letter_totals[letter] = total
    sorted_letters = sorted(letter_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    return ", ".join([f"{l.upper()}:{v:.1f}" for l, v in sorted_letters])

if __name__ == "__main__":
    model = WordleSolver()
    start_time = time.time()
    run_training_loop()
    end_time = time.time()
    print(end_time-start_time)
    model.save_weights()
   