import functools
import time

# TODO: do we need allowed_exceptions -> pass? Probably not.
def retry(timeout=30, delay=5, retry_fail_exceptions=()):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            cnt = 0
            result = None

            t0 = time.monotonic()
            while True:
                try:
                    cnt += 1
                    result = fn(*args, **kwargs)
                except retry_fail_exceptions:
                    raise
                except Exception as e:
                    print('try #{count} of {fn}(args={args}, kwargs={kwargs}) failed: {type}: {reason} '.format(
                        count=cnt,
                        fn=fn,
                        args=args,
                        kwargs=kwargs,
                        type=type(e),
                        reason=str(e),
                    ))

                    td = time.monotonic() - t0
                    if td > timeout:
                        print(
                            'failing {} after {} attempts in '
                            '{} seconds'.format(fn, cnt, int(td)),
                        )
                        raise

                    time.sleep(delay)
                else:
                    break

            if cnt > 1:
                td = time.monotonic() - t0
                print(
                    'completed {} after {} attempts in '
                    '{} seconds'.format(fn, cnt, int(td)),
                )
            return result

        return wrapper
    return decorator


@retry(timeout=10, delay=1, retry_fail_exceptions=(TypeError,))
def my_fn():
    rint = randint(1, 3)
    if rint == 1:
        print('RAISING VALUE ERROR, retry...')
        raise ValueError('spagon value error')
    elif rint == 2:
        print('RAISING TYPE ERROR, SHOULD FAIL RETRY')
        raise TypeError('spagon type error!')
    print('we did okay!')
    return 'Spagon'


def main():
    res = my_fn()
    print('result:', res)

# Example output:
"""
mspagon:~$ python3 retry.py
RAISING VALUE ERROR, retry...
try #1 of <function my_fn at 0x7ffff66987b8>(args=(), kwargs={}) failed: <class 'ValueError'>: spagon value error
we did okay!
completed <function my_fn at 0x7ffff66987b8> after 2 attempts in 1 seconds
result: Spagon
"""
