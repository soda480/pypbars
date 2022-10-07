from multiprocessing import Pool  # pragma: no cover
from queue import Empty  # pragma: no cover
from multiprocessing import cpu_count  # pragma: no cover
from multiprocessing import get_context  # pragma: no cover
from list2term.multiprocessing import LinesQueue  # pragma: no cover
from list2term.multiprocessing import QueueManager  # pragma: no cover
from list2term.multiprocessing import lines  # pragma: no cover
from list2term.multiprocessing import CONCURRENCY  # pragma: no cover
from pypbars import ProgressBars  # pragma: no cover


def progress_bars(function, iterable, lookup=None, **kwargs):  # pragma: no cover
    """ multiprocessing enabled helper function to display progress bars from Pool of processes to terminal
        returns multiprocessing.pool.AsyncResult
    """
    QueueManager.register('LinesQueue', LinesQueue)
    with QueueManager() as manager:
        lines_queue = manager.LinesQueue(ctx=get_context())
        with Pool(CONCURRENCY) as pool:
            # add lines_queue to each process arguments list
            # the function should write status messages to the queue
            process_data = [item + (lines_queue,) for item in iterable]
            # start process pool asynchronously
            results = pool.starmap_async(function, process_data)
            if not lookup:
                # create lookup list consisting of colon-delimeted string of iterable arguments
                lookup = [':'.join(map(str, item)) for item in iterable]
            # display progress bars from pool processes to the terminal using ProgressBars
            # read message from lines queue and write it to the respective progress bar on the terminal
            with ProgressBars(lookup=lookup, **kwargs) as terminal_progress_bars:
                while True:
                    try:
                        terminal_progress_bars.write(lines_queue.get(timeout=.1))
                    except Empty:
                        if results.ready():
                            break
    return results
