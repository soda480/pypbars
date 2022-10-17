import time, random, logging
from multiprocessing import Queue
from queue import Empty
import names
from faker import Faker
from multiprocessing import Pool
from multiprocessing import get_context
from multiprocessing import cpu_count
from list2term.multiprocessing import LinesQueue
from list2term.multiprocessing import QueueManager
from queue import Empty
from pypbars import ProgressBars
logger = logging.getLogger(__name__)

def prepare_queue(queue):
    for _ in range(75):
        queue.put({'total': random.randint(100, 150)})

def do_work(worker_id, total, logger):
    logger.write(f'{worker_id}->worker is {names.get_full_name()}')
    logger.write(f'{worker_id}->processing total of {total} items')
    for index in range(total):
        # simulate work by sleeping
        time.sleep(random.choice([.001, .003, .005, .009]))
        logger.write(f'{worker_id}->processed {index}')
    return total

def run_q(worker_id, queue, logger):
    result = 0
    while True:
        try:
            total = queue.get(timeout=1)['total']
            result += do_work(worker_id, total, logger)
            logger.write(f'{worker_id}->reset')
        except Empty:
            break
    return result

def main():
    QueueManager.register('LinesQueue', LinesQueue)
    QueueManager.register('Queue', Queue)
    with QueueManager() as manager:
        queue = manager.LinesQueue(ctx=get_context())
        data_queue = manager.Queue()
        prepare_queue(data_queue)
        with Pool(3) as pool:
            print(f'>> Processing {data_queue.qsize()} sets using 3 workers ...')
            process_data = [(Faker().name(), data_queue, queue) for index in range(3)]
            results = pool.starmap_async(run_q, process_data)
            lookup = [f'{data[0]}' for data in process_data]
            with ProgressBars(lookup=lookup, show_prefix=False, show_fraction=False, use_color=True) as lines:
                while True:
                    try:
                        item = queue.get(timeout=.1)
                        if item.endswith('->reset'):
                            index, message = lines.get_index_message(item)
                            lines[index].reset(clear_alias=False)
                        else:
                            lines.write(item)
                    except Empty:
                        if results.ready():
                            # create method to complete all
                            lines[0].complete = True
                            lines[1].complete = True
                            lines[2].complete = True
                            break
    return sum(results.get())


if __name__ == '__main__':
    results = main()
    print(f">> 3 workers processed a total of {results} items")
