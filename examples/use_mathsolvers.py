import mathsolvers


def direct_use_with_care():
    # Получить объект --- это просто solver
    mathsolvers.pprint(mathsolvers.solver(r'<<units 3ар \\ дм^2>>'))

    # Отформатировать как схему:
    print(mathsolvers.to_text(mathsolvers.solver('<<solve 2x+1=3>>')))


def worker_use_with_timeout():
    """
    Использование worker'а для ограничения по времени
    """
    # Импортировать mathsolvers при этом не нужно, нужно импортировать только
    # "лёгкого" воркера. Тяжёлый импорт он будет делать в другом процессе
    from mathsolvers import math_worker

    worker = math_worker.MathWorker()
    print(worker.solver(r'<<compare 2/3 \\ 5/6>>'))
    print(worker.solver(r'<<simplify 99^99^99^99^99^99^99>>'))
    print(worker.to_text(worker.solver('<<factor 60>>')))
    print(worker.embed_solvers('<<simplify 2x+3x>>\n<<simplify 2x * 3x>>'))
    try:
        print(worker.embed_solvers('<<simplify 2x+3x>>\n<<simplify 99^99^99^99^99^99^99>>'))
    except Exception as e:
        print('ERROR:', e)
        print('Таймаут --- это правильно!')
    worker.shutdown()


def main():
    direct_use_with_care()
    worker_use_with_timeout()


if __name__ == '__main__':
    main()
