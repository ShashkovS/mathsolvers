import os

import pytest

dir_path = os.path.dirname(os.path.realpath(__file__))


def run_tests():
    # Аргументы для pytest
    pytest_args = ['-vvs', dir_path, '-n7', 'timeout', '5']

    # Запуск pytest
    result = pytest.main(pytest_args)

    # Обработка результата
    if result == 0:
        print('All tests passed.')
    else:
        print('Some tests failed.')
        exit(result)


if __name__ == '__main__':
    run_tests()
