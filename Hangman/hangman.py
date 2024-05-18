import requests
import json

# Get Secret word
res = requests.get(r"https://random-word-api.herokuapp.com/word")
response = json.loads(res.text)
secret_word = response[0].upper()

# Global Variables
protected_word = "_" * len(secret_word)
guesses = 6
previous_guesses = []
failed_guesses = []

def get_guess():
    global guesses
    guess = None
    while True:
        try:
            # Returns a guess that is either a letter in the alphabet or the secret word itself
            guess = input(f"You have {guesses} incorrect guesses remaining. Make a guess: ").upper()
            if (len(guess) > 1 and guess != secret_word) or not guess.isalpha():
                raise Exception()
            # Check if the user already inputted the guess
            elif guess in previous_guesses:
                raise RuntimeError
            previous_guesses.append(guess)
            return guess
        except RuntimeError:
            print(f"You have already guessed {guess}.")
        except:
            print(f'"{guess}" is not a valid guess.')

# Print the current state of the word and the incorrect guesses
def print_protected_word():
    global failed_guesses, protected_word
    space_sep = ' '.join(list(protected_word))
    print(space_sep, end="  ")
    
    # print incorrect guesses
    if len(failed_guesses) > 0:
        print("Incorrect:", end=" ")
        for incorrect_guess in failed_guesses:
            print(incorrect_guess, end=" ")
    print()

# Win Condition + Uncover bits of the protected_word
# Returns True if the player won
def handle_guess(guess):
    global failed_guesses, protected_word, guesses

    if not (guess in secret_word):
        guesses -= 1
        failed_guesses.append(guess)
        return False

    # if user guesses the entire word correctly
    if guess == secret_word:
        protected_word = " ".join(list(secret_word))
        return True

    # for single characters
    list_version = list(protected_word)
    for idx, char in enumerate(secret_word):
        # Only substitute '_' where the letter is in the secret_word
        if char == guess:
            list_version[idx] = guess
    protected_word = "".join(list_version)

    return not ("_" in protected_word)


def main():
    print("I'm thinking of a secret word. Guess one letter at a time until you reveal the whole word.")
    print_protected_word()

    while guesses > 0:
        guess = get_guess()
        correct_guess = handle_guess(guess)
        print_protected_word()

        if correct_guess:
            print("Congratulations! You have guessed the secret word!")
            break

    if guesses == 0:
        print(f"You Lost. The correct word was {secret_word}.")


if __name__ == "__main__":
    main()
