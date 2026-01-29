import signal
import pyperclip
import json

import mathsolvers

# from mathsolvers.solvers.simplification import _counted
_counted = {}


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    print('alarm!', flush=True)
    raise TimeoutException()


def main():
    # worker = mathsolvers.MathWorker()
    unique = set()
    trues = []
    cnt = 0
    schemes = []
    scheme_jsons = []
    for line in open('mega_pool.txt', encoding='utf-8'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)
        good = False
        try:
            sol = mathsolvers.solver(line)
            txt = mathsolvers.to_text(sol)
            escaped = '"' + txt.replace('"', '""') + '"'
            schemes.append(escaped)
            only_steps = {k: v for k, v in sol.items() if k.startswith('step')}
            only_steps_s = '"' + json.dumps(only_steps, ensure_ascii=False, indent=2).replace('"', '""') + '"'
            scheme_jsons.append(only_steps_s)
            if sol.get('good_scheme'):
                line = line.strip()
                solver = line.split(' ', maxsplit=1)[0][2:]
                # print(line)
                tp = mathsolvers.classify_math(solver, line, sol)
                row = f'{solver}\t{tp}\t{line}'
                unique.add(row)
                good = True
                # print(line.strip(), mathsolvers.classify_math())
            # print(sol)
        except Exception as e:
            print(line, e)
            raise
        finally:
            signal.alarm(0)
        # print(good)
        trues.append(good)
        cnt += 1
        # if cnt % 100 == 0:
        #     print(cnt, line.strip())
        # break
    # pyperclip.copy('\n'.join(unique))
    # pyperclip.copy('\n'.join(schemes))
    pyperclip.copy('\n'.join(scheme_jsons))
    # pyperclip.copy('\n'.join(map(str, trues)))
    print('in clipboard')
    data = [(str(cng)[7:], conv, cnt) for (cng, conv), cnt in _counted.items()]
    data.sort(key=lambda trip: (trip[0], -trip[2], len(trip[1]), trip[1]))
    return data


if __name__ == '__main__':
    data = main()
    # with open('mega_poot_ops.txt', 'w', encoding='utf-8') as f:
    #     for cng, conv, cnt in data:
    #         # print(f'{cng} {cnt} {conv}')
    #         print(f'{cng} {cnt} {conv}', file=f)
