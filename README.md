# pypbars
[![build](https://github.com/soda480/pypbars/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/soda480/pypbars/actions/workflows/main.yml)
[![Code Grade](https://api.codiga.io/project/33925/status/svg)](https://app.codiga.io/public/project/33925/pypbars/dashboard)
[![codecov](https://codecov.io/gh/soda480/pypbars/branch/main/graph/badge.svg?token=1G4T6UYTEX)](https://codecov.io/gh/soda480/pypbars)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/pypbars.svg)](https://badge.fury.io/py/pypbars)
[![python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-teal)](https://www.python.org/downloads/)

The `pypbars` module provides a convenient way to dynamically display multiple progress bars to the terminal. The `pypbars.ProgressBars` class is a subclass of [l2term.Lines](https://pypi.org/project/l2term/) that displays a list to the terminal, and uses [progress1bar.ProgressBar](https://pypi.org/project/progress1bar/) to render the progress bar. The module also contains helper classes to facilitate displaying progress bars for worker processes in a [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool).

### Installation
```bash
pip install pypbars
```

#### [example1 - ProgressBars with asyncio](https://github.com/soda480/pypbars/blob/main/examples/example1.py)

Create `ProgressBars` using a lookup list containing unique values, these identifiers will be used to get the index of the appropriate `ProgressBar` to be updated. The convention is for the function to include `logger.write` calls containing the identifier and a message for when and how the respective progress bar should be updated. In this example the default `regex` dict is used but the caller can specify their own, so long as it contains regular expressions for how to detect when `total`, `count` and optional `alias` are set.

<details><summary>Code</summary>

```Python
import asyncio
import random
import uuid
from pypbars import ProgressBars

async def do_work(worker, logger=None):
    logger.write(f'{worker}->worker is {worker[0:random.randint(12, 36)]}')
    total = random.randint(10, 65)
    logger.write(f'{worker}->processing total of {total} items')
    for count in range(total):
        # mimic an IO-bound process
        await asyncio.sleep(random.choice([.1, .2, .3]))
        logger.write(f'{worker}->processed {count}')
    return total

async def run(workers):
    with ProgressBars(lookup=workers, show_prefix=False, show_fraction=False, ticker=9644) as logger:
        doers = (do_work(worker, logger=logger) for worker in workers)
        return await asyncio.gather(*doers)

def main():
    workers = [str(uuid.uuid4()) for _ in range(12)]
    print(f'Total of {len(workers)} workers working concurrently')
    results = asyncio.run(run(workers))
    print(f'The {len(workers)} workers processed a total of {sum(results)} items')

if __name__ == '__main__':
    main()
```

</details>

#### [example2 - ProgressBars with multiprocessing Pool](https://github.com/soda480/pypbars/blob/main/examples/example2.py)

This example demonstrates how `pypbars` can be used to display progress bars from processes executing in a multiprocessing Pool. The parent `l2term.multiprocessing` module contains helper classes that define a `LinesQueue` as well as a `QueueManager` to facilitate communication between worker processes and the main process. In this example, we leverage a Pool of workers to compute the number of prime numbers in a given number range. The worker processes are passed a queue that they write messages to, while the main process reads messages from the queue, interprets the message and updates the ProgressBar respectively. Note that each line represents a background worker process.

<details><summary>Code</summary>

```Python
import time
from multiprocessing import Pool
from multiprocessing import get_context
from multiprocessing import cpu_count
from l2term.multiprocessing import LinesQueue
from l2term.multiprocessing import QueueManager
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
    QueueManager.register('LinesQueue', LinesQueue)
    with QueueManager() as manager:
        queue = manager.LinesQueue(ctx=get_context())
        with Pool(CONCURRENCY) as pool:
            process_data = [(index, index + step, queue) for index in range(0, number, step)]
            results = pool.starmap_async(count_primes, process_data)
            lookup = [f'{data[0]}:{data[1]}' for data in process_data]
            with ProgressBars(lookup=lookup, show_prefix=False, show_fraction=False, use_color=True) as lines:
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
```

</details>

![example2](https://raw.githubusercontent.com/soda480/pypbars/main/docs/images/example2.gif)

### Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
-t \
pypbars:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-v $PWD:/code \
pypbars:latest \
bash
```

Execute the build:
```sh
pyb -X
```
