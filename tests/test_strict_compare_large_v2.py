import pytest
import json

import mathsolvers
from mathsolvers import CompareVerdict

"""
from python_calamine import CalamineWorkbook
import json
workbook = CalamineWorkbook.from_path(r'all_prod_ver_data.xlsx')
data = []
for i, row in enumerate(workbook.get_sheet_by_index(0).iter_rows()):
    if i < 1:
        continue
    user_ans = str(row[1])
    corr_ans = str(row[2])
    are_eq = int(row[3])
    data.append({'user_ans': user_ans, 'corr_ans': corr_ans, 'are_eq': are_eq})
with open(r'strict_compare_pool.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
"""


def _run_on_data(data):
    ok_compared_as_ok = []
    ok_compared_as_not = []
    not_compared_as_ok = []
    not_compared_as_not = []
    tot_oks = tot_nots = 0
    for row in data:
        cmp: CompareVerdict = mathsolvers.strict_compare_v2(row['user_ans'], row['corr_ans'])
        is_ok = row['are_eq']
        tot_oks += is_ok == 1
        tot_nots += is_ok == 0
        if is_ok == 0 and cmp == CompareVerdict.NOT_EQUAL:
            not_compared_as_not.append(row)
        elif is_ok == 0 and cmp == CompareVerdict.EQUAL:
            not_compared_as_ok.append(row)
        elif is_ok == 1 and cmp == CompareVerdict.NOT_EQUAL:
            ok_compared_as_not.append(row)
        elif is_ok == 1 and cmp == CompareVerdict.EQUAL:
            ok_compared_as_ok.append(row)
    print(len(ok_compared_as_ok), len(ok_compared_as_not), len(not_compared_as_ok), len(not_compared_as_not))
    assert len(ok_compared_as_ok) / tot_oks >= 0.7, 'Должно засчитываться >= 70% ok-ok тестов'
    assert len(not_compared_as_not) / tot_nots >= 0.3, 'Должно отклоняться >= 30% not-not тестов'
    assert len(not_compared_as_ok) == 0, 'Ни один не-ок тест не должен проходить как ок. А прошли:\n' + json.dumps(
        not_compared_as_ok, ensure_ascii=False, indent=2)


# @pytest.mark.skip(reason="Отключен для ускорения")
@pytest.mark.timeout(60)
def test_strict_compare_v2_pool_p1():
    data = json.load(open('strict_compare_pool.json'))
    _run_on_data(data[::3])


# @pytest.mark.skip(reason="Отключен для ускорения")
@pytest.mark.timeout(60)
def test_strict_compare_v2_pool_p2():
    data = json.load(open('strict_compare_pool.json'))
    _run_on_data(data[1::3])


# @pytest.mark.skip(reason="Отключен для ускорения")
@pytest.mark.timeout(60)
def test_strict_compare_v2_pool_p3():
    data = json.load(open('strict_compare_pool.json'))
    _run_on_data(data[2::3])
