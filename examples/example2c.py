import time
from multiprocessing import Pool
from multiprocessing import Queue
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

def count_primes(workerid, start, stop, logger):
    logger.write(f'{workerid}->worker is {start}:{stop}')
    logger.write(f'{workerid}->processing total of {stop - start} items')
    primes = 0
    for number in range(start, stop):
        if is_prime(number):
            primes += 1
        logger.write(f'{workerid}->processed {number}')
    return primes

def run_q(workerid, data_queue, logger):
    total = 0
    while True:
        try:
            item = data_queue.get(timeout=1)
            start = item['start']
            stop = item['stop']
            total += count_primes(workerid, start, stop, logger)
            logger.write(f'{workerid}->reset')
        except Empty:
            break
    return total

def main(number):
    step = int(number / CONCURRENCY)
    processes = 3
    print(f"Adding {int(number / step)} ranges into a data queue that {processes} workers will work from until empty")
    QueueManager.register('LinesQueue', LinesQueue)
    QueueManager.register('Queue', Queue)
    with QueueManager() as manager:
        lines_queue = manager.LinesQueue(ctx=get_context())   
        # prepare data queue
        data_queue = manager.Queue()
        for index in range(0, number, step):
            data_queue.put({'start': index, 'stop': index + step})
        with Pool(processes) as pool:
            process_data = [(workerid, data_queue, lines_queue) for workerid in range(processes)]
            results = pool.starmap_async(run_q, process_data)
            lookup = [f'{data[0]}' for data in process_data]
            with ProgressBars(lookup=lookup, show_prefix=False, show_fraction=False, use_color=True, show_duration=True, clear_alias=True) as lines:
                while True:
                    try:
                        item = lines_queue.get(timeout=.1)
                        if item.endswith('->reset'):
                            index, message = lines.get_index_message(item)
                            lines[index].reset(clear_alias=False)
                        else:
                            lines.write(item)
                    except Empty:
                        if results.ready():
                            for index, _ in enumerate(lines):
                                lines[index].complete = True
                            break
    return sum(results.get())

if __name__ == '__main__':
    start = time.perf_counter()
    number = 50_000
    result = main(number)
    stop = time.perf_counter()
    print(f"Finished in {round(stop - start, 2)} seconds\nTotal number of primes between 0-{number}: {result}")
