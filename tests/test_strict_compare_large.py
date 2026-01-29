import pytest
import json

import mathsolvers

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


# @pytest.mark.skip(reason="Отключен для ускорения")
@pytest.mark.timeout(30)
def test_strict_compare_pool():
    ok_compared_as_ok = []
    ok_compared_as_not = []
    not_compared_as_ok = []
    not_compared_as_not = []
    data = json.load(open('strict_compare_pool.json'))
    for row in data:
        cmp = int(mathsolvers.strict_compare(row['user_ans'], row['corr_ans']))
        is_ok = row['are_eq']
        if is_ok == 0 and cmp == 0:
            not_compared_as_not.append(row)
        elif is_ok == 0 and cmp == 1:
            not_compared_as_ok.append(row)
        elif is_ok == 1 and cmp == 0:
            ok_compared_as_not.append(row)
        elif is_ok == 1 and cmp == 1:
            ok_compared_as_ok.append(row)

    tot_oks = len(ok_compared_as_ok) + len(ok_compared_as_not)
    print(len(ok_compared_as_ok), len(ok_compared_as_not), len(not_compared_as_ok), len(not_compared_as_not))
    assert len(ok_compared_as_ok) / tot_oks >= 0.7, 'Должно засчитываться >= 70% ok-ok тестов'
    assert len(not_compared_as_ok) == 0, 'Ни один не-ок тест не должен проходить как ок. А прошли:\n' + json.dumps(
        not_compared_as_ok, ensure_ascii=False, indent=2)
