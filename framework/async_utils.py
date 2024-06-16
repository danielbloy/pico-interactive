# Because asyncio.wait() is not available in CircuitPython, it has been copied
# directly into here to make it available in that environment. Therefore, the
# following invocation:
#   done, pending = await asyncio.wait(tasks, timeout=0)
#
# Can be replaced directly with:
#   done, pending = await asyncio.wait(tasks, timeout=0)
#
from asyncio import coroutines
from asyncio import events
from asyncio import futures

FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'
ALL_COMPLETED = 'ALL_COMPLETED'


async def wait(fs, *, timeout=None, return_when=ALL_COMPLETED):
    """Wait for the Futures or Tasks given by fs to complete.

    The fs iterable must not be empty.

    Coroutines will be wrapped in Tasks.

    Returns two sets of Future: (done, pending).

    Usage:

        done, pending = await asyncio.wait(fs)

    Note: This does not raise TimeoutError! Futures that aren't done
    when the timeout occurs are returned in the second set.
    """
    if futures.isfuture(fs) or coroutines.iscoroutine(fs):
        raise TypeError(f"expect a list of futures, not {type(fs).__name__}")
    if not fs:
        raise ValueError('Set of Tasks/Futures is empty.')
    if return_when not in (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED):
        raise ValueError(f'Invalid return_when value: {return_when}')

    fs = set(fs)

    if any(coroutines.iscoroutine(f) for f in fs):
        raise TypeError("Passing coroutines is forbidden, use tasks explicitly.")

    loop = events.get_running_loop()
    return await _wait(fs, timeout, return_when, loop)


async def _wait(fs, timeout, return_when, loop):
    """Internal helper for wait().

    The fs argument must be a collection of Futures.
    """
    assert fs, 'Set of Futures is empty.'
    waiter = loop.create_future()
    timeout_handle = None
    if timeout is not None:
        timeout_handle = loop.call_later(timeout, _release_waiter, waiter)
    counter = len(fs)

    def _on_completion(f):
        nonlocal counter
        counter -= 1
        if (counter <= 0 or
                return_when == FIRST_COMPLETED or
                return_when == FIRST_EXCEPTION and (not f.cancelled() and
                                                    f.exception() is not None)):
            if timeout_handle is not None:
                timeout_handle.cancel()
            if not waiter.done():
                waiter.set_result(None)

    for f in fs:
        f.add_done_callback(_on_completion)

    try:
        await waiter
    finally:
        if timeout_handle is not None:
            timeout_handle.cancel()
        for f in fs:
            f.remove_done_callback(_on_completion)

    done, pending = set(), set()
    for f in fs:
        if f.done():
            done.add(f)
        else:
            pending.add(f)
    return done, pending


def _release_waiter(waiter, *args):
    if not waiter.done():
        waiter.set_result(None)
