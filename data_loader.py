with open('valid-wordle-words.txt', 'r') as f:
    word_list = [line.strip() for line in f]
with open('shuffled_real_wordles.txt', 'r') as f:
    answer_list = [line.strip() for line in f]
alphabet = "abcdefghijklmnopqrstuvwxyz" 