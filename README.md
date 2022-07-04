# pypbars
[![build](https://github.com/soda480/pypbars/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/soda480/pypbars/actions/workflows/main.yml)
[![Code Grade](https://api.codiga.io/project/33925/status/svg)](https://app.codiga.io/public/project/33925/pypbars/dashboard)
[![codecov](https://codecov.io/gh/soda480/pypbars/branch/main/graph/badge.svg?token=1G4T6UYTEX)](https://codecov.io/gh/soda480/pypbars)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/pypbars.svg)](https://badge.fury.io/py/pypbars)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

The `pypbars` module provides a convenient way to dynamically display multiple progress bars to the terminal. The `pypbars.ProgressBars` class is a subclass of [l2term.Lines](https://pypi.org/project/l2term/) that displays lists to the terminal, and uses [progress1bar.ProgressBar](https://pypi.org/project/progress1bar/) to render the progress bar.

### Installation
```bash
pip install pypbars
```

#### [example1](https://github.com/soda480/pypbars/blob/main/examples/example1.py)

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

![example1](https://raw.githubusercontent.com/soda480/pypbars/main/docs/images/example1.gif)

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
