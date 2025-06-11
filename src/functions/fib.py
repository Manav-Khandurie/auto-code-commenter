def fibonacci(n, memo={}):
    """Calculate the nth Fibonacci number using memoization.

    Args:
        n (int): The index of the Fibonacci number to calculate.
        memo (dict, optional): Dictionary for memoization (stores previously computed results). 
                             Defaults to empty dict.

    Returns:
        int: The nth Fibonacci number.
    """
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]