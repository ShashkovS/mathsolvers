import logging
import multiprocessing.connection
import os


def worker_loop(pipe_worker: multiprocessing.connection.Connection):
    import mathsolvers

    logging.warning('MathWorker loop started. Pid=%s, ppid=%s', os.getpid(), os.getppid())
    while True:
        task_id = None
        try:
            task_id, func_name, args, kwargs = pipe_worker.recv()
            if task_id is None:
                return  # Сигнал завершения
            func = getattr(mathsolvers, func_name)
            result = func(*args, **kwargs)
            pipe_worker.send((task_id, result))
        except Exception as e:
            pipe_worker.send((task_id, e))
