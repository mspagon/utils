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
