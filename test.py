import concurrent.futures
import time

import math

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419]


def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


def main():
    t0 = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print('%d is prime: %s' % (number, prime))

    # for number in PRIMES:
    #     prime = is_prime(number)
    #     print('%d is prime: %s' % (number, prime))

    print("time: %.6f" % (time.perf_counter() - t0))


if __name__ == '__main__':
    main()

# for = time: 3.236654 sec
# executor = time: 1.483386 sec
