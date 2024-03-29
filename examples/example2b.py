import time
from multiprocessing import Pool
from multiprocessing import get_context
from multiprocessing import cpu_count
from list2term.multiprocessing import LinesQueue
from list2term.multiprocessing import QueueManager
from queue import Empty
from pypbars import ProgressBars

CONCURRENCY = cpu_count()

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
    return primes

def main(number):
    step = int(number / CONCURRENCY)
    processes = 3
    print(f"Distributing {int(number / step)} ranges across {CONCURRENCY} workers running {processes} concurrently")
    QueueManager.register('LinesQueue', LinesQueue)
    with QueueManager() as manager:
        queue = manager.LinesQueue(ctx=get_context())
        with Pool(processes) as pool:
            process_data = [(index, index + step, queue) for index in range(0, number, step)]
            results = pool.starmap_async(count_primes, process_data)
            lookup = [f'{data[0]}:{data[1]}' for data in process_data]
            with ProgressBars(lookup=lookup, show_prefix=False, show_fraction=False, use_color=True, show_duration=True) as lines:
                while True:
                    try:
                        lines.write(queue.get(timeout=.1))
                    except Empty:
                        if results.ready():
                            break
    return sum(results.get())

if __name__ == '__main__':
    start = time.perf_counter()
    number = 50_000
    result = main(number)
    stop = time.perf_counter()
    print(f"Finished in {round(stop - start, 2)} seconds\nTotal number of primes between 0-{number}: {result}")
