import time
from pypbars import ProgressBars
from list2term.multiprocessing import pool_map
from list2term.multiprocessing import CONCURRENCY

def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            return False
    else:
        return True

def count_primes(start, stop, logger):
    workerid = f'{start}:{stop}'
    logger.write(f'{workerid}->worker is {workerid}')
    logger.write(f'{workerid}->processing total of {stop - start} items')
    primes = 0
    for number in range(start, stop):
        if is_prime(number):
            primes += 1
        logger.write(f'{workerid}->processed {number}')
    logger.write(f'{workerid}->{workerid} processing complete')
    return primes

def main(number):
    step = int(number / CONCURRENCY)
    iterable = [(index, index + step) for index in range(0, number, step)]
    lookup = [':'.join(map(str, item)) for item in iterable]
    progress_bars = ProgressBars(lookup=lookup, show_prefix=False, show_fraction=False, use_color=True, show_duration=True)
    # print to screen with progress bars context
    results = pool_map(count_primes, iterable, context=progress_bars)
    # print to screen without progress bars context
    # results = pool_map(count_primes, iterable)
    # do not print to screen
    # results = pool_map(count_primes, iterable, print_status=False)
    return sum(results.get())

if __name__ == '__main__':
    start = time.perf_counter()
    number = 50_000
    result = main(number)
    stop = time.perf_counter()
    print(f"Finished in {round(stop - start, 2)} seconds\nTotal number of primes between 0-{number}: {result}")
