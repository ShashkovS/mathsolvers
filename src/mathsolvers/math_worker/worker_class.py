import os
import multiprocessing
import multiprocessing.connection

from mathsolvers.math_worker import worker_module
from mathsolvers.solvers_stuff import res_convert

_TIMEOUT = 1.0
__all__ = ['MathWorker']


class MathWorker:
    pipe_worker: multiprocessing.connection.Connection | None
    pipe_manager: multiprocessing.connection.Connection | None
    process: multiprocessing.context.SpawnProcess | None
    ctx: multiprocessing.context.SpawnContext | None
    task_id: int
    method: str

    def __init__(self, method=None):
        self.ctx = None
        self.pipe_worker = None
        self.pipe_manager = None
        self.process = None
        self.task_id = 0
        if method:
            self.method = method
        elif hasattr(os, 'fork'):
            self.method = 'fork'
        else:
            self.method = 'spawn'

    def start_worker(self):
        if self.process is not None:
            return
        self.ctx = multiprocessing.get_context(self.method)  # Use 'spawn' start method on Windows
        self.pipe_worker, self.pipe_manager = self.ctx.Pipe()
        self.process = self.ctx.Process(target=worker_module.worker_loop, args=(self.pipe_worker,))
        self.process.start()

    def stop_worker(self):
        if self.process is not None and self.process.is_alive():
            self.pipe_manager.send((None, None, None, None))  # Отправляем сигнал завершения
            self.process.join(timeout=_TIMEOUT)
            if self.process.is_alive():
                self.process.kill()
        self.process = None

    def run_with_timeout(self, func_name: str, *args, timeout=_TIMEOUT, **kwargs) -> dict | str:
        self.start_worker()
        send_task_id = self.task_id = self.task_id + 1
        self.pipe_manager.send((send_task_id, func_name, args, kwargs))
        if self.pipe_manager.poll(timeout):
            res_task_id, result = self.pipe_manager.recv()
            if res_task_id != send_task_id:
                raise InterruptedError(f'Внутренняя ошибка: {send_task_id=} {res_task_id=}')
        else:
            # Произошел таймаут
            self.process.terminate()
            self.process.join()
            self.process = None
            return {'task': args, 'error': f'Таймаут {timeout}с при вычислении выражения'}
        if isinstance(result, Exception):
            return {'task': args, 'error': str(result)}
        return result

    def __del__(self):
        self.stop_worker()

    def shutdown(self):
        self.stop_worker()

    def format(self, expr: str, fmt: str, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('format', expr, fmt, timeout=timeout)

    def solve_eq(self, expr: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('solve_eq', expr, timeout=timeout)

    def subs(self, expr: str, vals: dict, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('subs', expr, vals, timeout=timeout)

    def calc(self, expr: str, vals: dict, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('calc', expr, vals, timeout=timeout)

    def units(self, expr: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('units', expr, timeout=timeout)

    def compare(self, expr: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('compare', expr, timeout=timeout)

    def simplify(self, expr: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('simplify', expr, timeout=timeout)

    def check_equivalence(self, expr1: str, expr2: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('check_equivalence', expr1, expr2, timeout=timeout)

    def factor(self, expr: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('factor', expr, timeout=timeout)

    def solve(self, expr: str, *other_exprs: str, vars: str | list[str] | None = None, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('solve', expr, timeout=timeout)

    def solver(self, expr: str, *, timeout=_TIMEOUT) -> dict:
        return self.run_with_timeout('solver', expr, timeout=timeout)

    def to_text(self, res: dict, *, timeout=_TIMEOUT) -> str:
        return res_convert.to_text(res)

    def embed_solvers(self, expr: str, *, timeout=_TIMEOUT) -> str:
        res = self.run_with_timeout('embed_solvers', expr, timeout=timeout)
        if isinstance(res, dict) and 'error' in res:
            raise ValueError(res['error'])
        return res

    def strict_compare_v2(self, expr1: str, expr2: str, *, timeout=_TIMEOUT):
        return self.run_with_timeout('strict_compare_v2', expr1, expr2, timeout=timeout)


if __name__ == '__main__':
    worker = MathWorker()
    print(worker.strict_compare_v2('1+2*3', '3\\cdot2 + 1'))
    print(worker.solver('<<simplify 2**10 >>'))
    print(worker.solver('<<simplify 2**1000**1000 >>'))
    print(worker.solver('<<simplify 2**10 >>'))
    print(worker.solver('<<simplify 2**10+ >>'))
    print(worker.solve('2x + 1 = 3'))
    print(worker.solver('<<simplify 2**10 >>'))
    print(worker.to_text(worker.solver('<<simplify 2**10 >>')))
    print(worker.embed_solvers('<<solve 2fx+1=3>>\n<<solve x^2=4>>'))
    try:
        print(worker.embed_solvers('<<solve 2x+1=3>>\n<<solve x^{2 >>'))
    except Exception as e:
        print(e)
    worker.shutdown()
