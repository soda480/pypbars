# pypbars
[![build](https://github.com/soda480/pypbars/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/soda480/pypbars/actions/workflows/main.yml)
[![Code Grade](https://api.codiga.io/project/34681/status/svg)](https://app.codiga.io/hub/project/34681/pypbars)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://pybuilder.io/)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/pypbars.svg)](https://badge.fury.io/py/pypbars)
[![python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-teal)](https://www.python.org/downloads/)

The `pypbars` module provides a convenient way to display progress bars for concurrent [asyncio](https://docs.python.org/3/library/asyncio.html) or [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool) processes. The `pypbars` class is a subclass of [list2term](https://pypi.org/project/list2term/) that displays a list to the terminal, and uses [progress1bar](https://pypi.org/project/progress1bar/) to render the progress bar.

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
from faker import Faker
from pypbars import ProgressBars

async def do_work(worker, logger=None):
    logger.write(f'{worker}->worker is {worker}')
    total = random.randint(10, 65)
    logger.write(f'{worker}->processing total of {total} items')
    for count in range(total):
        # mimic an IO-bound process
        await asyncio.sleep(.1)
        logger.write(f'{worker}->processed {count}')
    return total

async def run(workers):
    with ProgressBars(lookup=workers, show_prefix=False, show_fraction=False) as logger:
        doers = (do_work(worker, logger=logger) for worker in workers)
        return await asyncio.gather(*doers)

def main():
    workers = [Faker().user_name() for _ in range(10)]
    print(f'Total of {len(workers)} workers working concurrently')
    results = asyncio.run(run(workers))
    print(f'The {len(workers)} workers processed a total of {sum(results)} items')

if __name__ == '__main__':
    main()
```

</details>

![example1](https://raw.githubusercontent.com/soda480/pypbars/main/docs/images/example1.gif)

#### [example2 - ProgressBars with multiprocessing Pool](https://github.com/soda480/pypbars/blob/main/examples/example2.py)

This example demonstrates how `pypbars` can be used to display progress bars from processes executing in a [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#using-a-pool-of-workers). The `pypbars.multiprocessing` module contains a `progress_bars` method that fully abstracts the required multiprocessing constructs, you simply pass it the function to execute along with an iterable of arguments to pass each process invocation. The method will execute the functions asynchronously and return a multiprocessing.pool.AsyncResult object. Additional key word arguments can be passed to the `progress_bars` method to control `ProgressBars` instance.  Each line in the terminal represents a background worker process.

If you do not wish to use the abstraction, the `list2term.multiprocessing` module contains helper classes that define a `LinesQueue` as well as a `QueueManager` to facilitate communication between worker processes and the main process. Refer to [example3](https://github.com/soda480/pypbars/blob/main/examples/example3.py) for how the helper methods can be used. 

**Note** the function being executed must accept a `logger` object that is used to write status messages, this is the mechanism for how status messages are sent from the worker processes to the main process, it is the main process that is displaying the progress bars to the terminal. The messages must be written using the format `{identifier}->{message}`, where (by default) {identifier} is a colon delimited string consisting of the function arguments, it uniquely identifies a process to the ProgressBars instance. You may choose to define your own identifer so long as you provide it via the `lookup` argument to the `ProgressBars` class or `progress_bars` method.

<details><summary>Code</summary>

```Python
import time
from pypbars.multiprocessing import progress_bars
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
    return primes

def main(number):
    step = int(number / CONCURRENCY)
    iterable = [(index, index + step) for index in range(0, number, step)]
    results = progress_bars(count_primes, iterable, use_color=True, show_prefix=False, show_fraction=False)
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
