import random
import time
import sys
from data_loader import *
win_counter = 0
def start():
    answer = answer_list[random.randint(1,2316)]
    answer_letter_list = [letter.strip() for letter in answer]
    return answer_letter_list

def print_color_coded_words(letters, scores):
    sys.stdout.write("\033[F")
    sys.stdout.flush()
    bg_colors = {
        1: "\033[48;5;242m", 
        2: "\033[43m",       
        3: "\033[42m",       
    }
    reset = "\033[0m"
    
    result_string = ""
    
    for i in range(len(letters)):
        sys.stdout.write(f"\033[{i*3}D")
        sys.stdout.write("\033[K")
        sys.stdout.flush()
        letter = letters[i].upper()
        color = bg_colors.get(scores[i], "")

        result_string += f"{color} {letter} {reset}"
    
        sys.stdout.write(result_string)
        sys.stdout.flush()
        time.sleep(0.2)



def result(letter_list,answer_letter_list):
    points = [1] * 5
    temp_answer = list(answer_letter_list)
    for i in range(5):
        if letter_list[i] == answer_letter_list[i]:
            points[i]=3
            temp_answer[i]= None
    for i in range(5):
        if points[i]==3:
            continue
        letter = letter_list[i]
        if letter in temp_answer:
            points[i] = 2
            temp_answer.remove(letter)
    return points

def game_ai(ai_guess):
    global win_counter
    current_answer = start()
    guess_count = 0
    if ai_guess:
        ai_guess.reset()
    else:
        guess = input()
    while guess_count < 6:
        guess_count+=1
        if ai_guess:
            guess = ai_guess.get_guess(guess_count)
        if len(guess) == 5:
            if guess in word_list:
                letter_list = [letter.strip() for letter in guess]
                points = result(letter_list,current_answer)
                print_color_coded_words(letter_list, points)
                sys.stdout.write("\n")
                if sum(points) == 15:
                    win = True
                    break
            else:
                guess_count-=1
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                sys.stdout.write("\033[F")
                
        else:
            guess_count-=1
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            sys.stdout.write("\033[F")
        sys.stdout.write("\n")
        sys.stdout.flush()
        sys.stdout.write("\033[15D")
        sys.stdout.flush()
        win = False
        if ai_guess:
            ai_guess.update(guess,points)

    if win == True:
        win = False
        win_counter +=1
        print(f"""\nYou Won, good job, wanna play again? (Y/N)
Win counter: {win_counter}   
""")
    else:
        word = "".join(current_answer)
        print(f"You lost, the word was {word.upper()}, wanna play again?(Y/N)")
    option = "" 
    while option not in ["Y","N"]:
        option = input().upper() if not ai_guess else "Y"
        if option == "Y":
            game_ai(ai_guess)
        if option == "N":
            exit()    
def game():
    global win_counter
    current_answer = start()
    guess_count = 0
    while guess_count < 6:
        print(guess_count)
        guess_count+=1
        guess = input().lower()
        if len(guess) == 5:
            if guess in word_list:
                letter_list = [letter.strip() for letter in guess]
                points = result(letter_list,current_answer)
                print_color_coded_words(letter_list, points)
                if sum(points) == 15:
                    win = True
                    break
            else:
                guess_count-=1
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                sys.stdout.write("\033[F")
                
        else:
            guess_count-=1
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            sys.stdout.write("\033[F")
        sys.stdout.write("\033[B")
        sys.stdout.write("\033[15D")
        sys.stdout.flush()
        win = False


    if win == True:
        win = False
        win_counter +=1
        print(f"""\nYou Won, good job, wanna play again? (Y/N)
Win counter: {win_counter}   
""")
    else:
        word = "".join(current_answer)
        print(f"You lost, the word was {word.upper()}, wanna play again?(Y/N)")
    option = ""
    while option not in ["Y","N"]:
        option = input().upper()
        if option == "Y":
            game()
        if option == "N":
            exit()    

if __name__  == "__main__":
    game()   