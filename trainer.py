from config import *
import random
from data_loader import *
from wordle import result
from model import WordleSolver
from wordle_solver import generate_training, alphabet, game_state
x_train, y_targets = generate_training()
model = WordleSolver(len(alphabet))
def run_training_loop():
    print(f"Starting training (LR: {LEARNING_RATE})")
    x_train, y_train = generate_training()
    for epoch in range(EPOCHS):
        hit_count = 0
        epoch_loss = 0
        point_count = 0
        for i in range(len(x_train)):
            state = x_train[i]
            for char_idx, score in enumerate(state[:26]):
                if score >= 1:
                    if score >1:
                        point_count +=1
                    loss = model.train_step(char_idx, score)
                    epoch_loss += loss
                    hit_count+=1
        avg_loss = epoch_loss / hit_count if hit_count > 0 else 0
        print(f"Epoch {epoch+1}/{EPOCHS} | Updates: {hit_count} | Avg Loss: {avg_loss:.6f}")
        
        print(f"Epoch {epoch+1} complete. AL: {epoch_loss/NUM_SAMPLES:.4f}")
    print(f"Hit count:{point_count}")
def train():
    print (f"\n Starting training\nLearning rate: {LEARNING_RATE}")

    for i in range(len(x_train)):
        state = x_train[i]
        for idx,score in enumerate(state[:26]):
            if score >1:
                loss = model.train_step(idx,score)
                total_loss += loss
            if (i + 1) % 20 == 0:
                print(f"Sample{i+1}/{len(x_train)} | AVG Loss: {total_loss/(i+1):.4f}")
        
    print("Training done")
    return model
def generate_game_training(solver):
    for _ in range(NUM_SAMPLES):
        target = random.choice(answer_list)
        solver.reset()
        
        while len(solver.history) < 6:
            state = game_state(target, [g for g, p in solver.history])
            list_before = len(solver.possible_words)
            
            guess = solver.get_guess()
            points = result(list(guess), list(target))
            solver.update(guess, points)
            
            list_after = len(solver.possible_words)
            won = (sum(points) == 15)
            
            solver.train_on_game(state, guess, list_before, list_after, won)
            
            if won: break
if __name__ == "__main__":
    model = WordleSolver(26)
    model.load_weights()
    run_training_loop()
    model.save_weights()
    print("\n--- AI'S TOP VALUED LETTERS ---")

    results = []
    for i, char in enumerate(alphabet):
        results.append((char, model.weights[i][0]))


    results.sort(key=lambda x: x[1], reverse=True)

    for char, weight in results[:10]:
        print(f"Letter: {char.upper()} | Value: {weight:.4f}")