import random

credits = 500
play_again = True

while play_again:

    while True:
        try:
            bet = int(input(f"You have {credits} credits. How many would you like to bet? "))
            break
        except:
            print("Invalid bet.")
    random_number = random.randint(1, 100)
    guesses = 6
    print(f"I'm thinking of a number between 1 and 100. You have {guesses} guesses.")

    while guesses:
        try:
            guess = int(input("Enter a number: "))

            if guess > 100 or guess < 1:
                raise Exception()
            elif guess > random_number:
                guesses -= 1
                print(f"Too high! You have {guesses} guesses left.")
            elif guess < random_number:
                guesses -= 1
                print(f"Too low! You have {guesses} guesses left.")
            else:
                break

        except:
            print(f"Invalid number. You have {guesses} guesses left.")

    if guesses == 0:
        credits -= bet
        print(f"You lose! The correct number was {random_number}.")
        print(f"You lose {bet} credits.", end=" ")
    else:
        credits += bet
        print(f"Correct! You win {bet} credits.", end=" ")
    print(f"You now have {credits} credits.")

    if credits <= 0:
        break

    play_again = input("Would you like to play again (Y/N)? ") == 'Y'
