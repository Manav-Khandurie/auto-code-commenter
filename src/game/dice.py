import random
import math

def roll_dice(sides=6):
    """Roll a dice with a specified number of sides and return the result."""
    return random.randint(1, sides)

def factorial(n):
    """Calculate the factorial of a non-negative integer n."""
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
    if n == 0:
        return 1
    return n * factorial(n - 1)

def draw_card():
    """Draw a random card from a standard deck of playing cards.
    
    Returns:
        str: A string representing the drawn card in the format 'Rank of Suit'.
    """
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    
    rank = random.choice(ranks)
    suit = random.choice(suits)
    
    return f"{rank} of {suit}"

def calculate_pi(terms=1000):
    """Estimate the value of Pi using the Gregory-Leibniz series.
    
    Args:
        terms (int): Number of terms to use in the series approximation.
        
    Returns:
        float: The estimated value of Pi.
    """
    pi_estimate = 0
    for i in range(terms):
        # Alternate between adding and subtracting terms in the series
        pi_estimate += ((-1) ** i) / (2 * i + 1)
    return 4 * pi_estimate

def simulate_game():
    """Simulate a game that involves rolling a dice, calculating a factorial, 
    drawing a card, and estimating Pi. Prints the results of each operation."""
    dice_roll = roll_dice()  # Roll a dice to get a random number
    fact_result = factorial(dice_roll)  # Calculate the factorial of the rolled number
    card = draw_card()  # Draw a random card from the deck
    pi_value = calculate_pi()  # Estimate the value of Pi
    
    print(f"Dice Roll: {dice_roll}")
    print(f"Factorial of {dice_roll}: {fact_result}")
    print(f"Drawn Card: {card}")
    print(f"Estimated Pi Value: {pi_value}")

if __name__ == "__main__":
    simulate_game()