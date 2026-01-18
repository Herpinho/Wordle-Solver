from wordle_solver import reset_ai
from model import WordleSolver
import numpy as np
import sys
import os
import time
hi_wr = 0
lo_avg = 0
counter = 0

wr_top5 = [99.165, 99.165, 99.165, 99.165, 99.165]
avg_top5 = [3.7258, 3.7988, 3.8002, 3.8391, 3.84345]
def loop_ai():
    start = time.time()
    hi_wr = 0
    lo_avg = 0
    counter = 0
    solver = WordleSolver()
    while True:
        print('\n\n\n\n')
        reset_ai(solver)
        print('\n\n\n\n')
        if solver.winrate >=99:
            for i in range(5):
                if solver.winrate>wr_top5[4-i]:         
                    wr_top5[4-i] = solver.winrate
                    hi_wr +=1
                    file_path = F"GEN_1/Winrate/{hi_wr}_AI_{solver.winrate:.2f}WR_{solver.average:.2f}average"
                    os.makedirs(file_path, exist_ok=True)
                    np.save(os.path.join(file_path, "wordle_weights.npy"), solver.weights)
                    np.save(os.path.join(file_path, "pair_weights.npy"), solver.pair_weights)
                    break

        if solver.average <=3.85:
            
            for i in range(5):
                if solver.average<avg_top5[i]:
                    avg_top5[i] = solver.average
                    lo_avg +=1
                    file_path = f"GEN_1/Average/{lo_avg}_AI_{solver.winrate:.2f}WR_{solver.average:.2f}average"
                    os.makedirs(file_path, exist_ok=True)
                    np.save(os.path.join(file_path, "wordle_weights.npy"), solver.weights)
                    np.save(os.path.join(file_path, "pair_weights.npy"), solver.pair_weights)
                    break
        counter+=1
        sys.stdout.write(f"\r{counter} Total AIs Tested | {hi_wr + lo_avg} AIs Passed | {counter - (hi_wr + lo_avg)} AIs Deleted | Time elapsed: {time.time()-start:.0f}")
        sys.stdout.flush()
        print('\n')
        print(avg_top5)
        print(wr_top5)
loop_ai()