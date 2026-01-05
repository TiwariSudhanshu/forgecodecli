def fibonacci_sequence(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    else:
        list_fib = [0, 1]
        while len(list_fib) < n:
            next_fib = list_fib[-1] + list_fib[-2]
            list_fib.append(next_fib)
        return list_fib

# Find the first 10 Fibonacci numbers
n_fibonacci = 10
fib_numbers = fibonacci_sequence(n_fibonacci)

print(f"The first {n_fibonacci} Fibonacci numbers are: {fib_numbers}")