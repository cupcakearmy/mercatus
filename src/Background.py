import asyncio
import threading


def interval(every: float or int, autorun=False, iterations=-1, isolated=False, *args_root, **kwargs_root):
    def wrapper(fn):

        async def decorator(*args, **kwargs):
            it = 0
            first = True
            while iterations == -1 or it < iterations:
                it += 1

                if first:
                    first = False
                else:
                    await asyncio.sleep(every)

                await fn(*args, **kwargs)

        def capsule(*args, **kwargs):
            def loop_in_thread(l):
                asyncio.set_event_loop(l)
                l.run_until_complete(decorator(*args, **kwargs))

            loop = asyncio.get_event_loop()
            threading.Thread(target=loop_in_thread, args=(loop,)).start()

        if autorun:
            if isolated:
                capsule(*args_root, **kwargs_root)
            else:
                asyncio.run(decorator(*args_root, **kwargs_root))
        else:
            return capsule if isolated else decorator

    return wrapper
