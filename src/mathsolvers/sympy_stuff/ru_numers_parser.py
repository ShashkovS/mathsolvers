import re

from mathsolvers.sympy_stuff.any_text_parser import build_trie, trie_to_regex

_denom_numbers = {
    'вторых': '2',
    'вторая': '2',
    'третьих': '3',
    'третья': '3',
    'четвертых': '4',
    'четвертая': '4',
    'четвёртых': '4',
    'четвёртая': '4',
    'пятых': '5',
    'пятая': '5',
    'шестых': '6',
    'шестая': '6',
    'седьмых': '7',
    'седьмая': '7',
    'восьмых': '8',
    'восьмая': '8',
    'девятых': '9',
    'девятая': '9',
    'десятых': '10',
    'десятая': '10',
    'одиннадцатых': '11',
    'одиннадцатая': '11',
    'двенадцатых': '12',
    'двенадцатая': '12',
    'тринадцатых': '13',
    'тринадцатая': '13',
    'четырнадцатых': '14',
    'четырнадцатая': '14',
    'пятнадцатых': '15',
    'пятнадцатая': '15',
    'шестнадцатых': '16',
    'шестнадцатая': '16',
    'семнадцатых': '17',
    'семнадцатая': '17',
    'восемнадцатых': '18',
    'восемнадцатая': '18',
    'девятнадцатых': '19',
    'девятнадцатая': '19',
    'двадцатых': '20',
    'двадцатая': '20',
    'тридцатых': '30',
    'тридцатая': '30',
    'сороковых': '40',
    'сороковая': '40',
    'пятидесятых': '50',
    'пятидесятая': '50',
    'шестидесятых': '60',
    'шестидесятая': '60',
    'семидесятых': '70',
    'семидесятая': '70',
    'восьмидесятых': '80',
    'восьмидесятая': '80',
    'девяностых': '90',
    'девяностая': '90',
    'сотых': '100',
    'сотая': '100',
}

_prefix_trie_with_denom_words = build_trie(s.lower() for s in _denom_numbers)
_regex_pattern_with_denom_words = trie_to_regex(_prefix_trie_with_denom_words)
_re_denom_words = re.compile(fr'(\d\s*)?\b({_regex_pattern_with_denom_words})\b', flags=re.IGNORECASE)


def _denom_words_replacer(match):
    rep = _denom_numbers[match.group(2).lower()]
    if match.group(1):
        return f'{match.group(1)}/{rep}'
    else:
        return f' 1/{rep}'


_number_words = {
    "ноль": 0,
    "один": 1, "одна": 1, "одно": 1,
    "два": 2, "две": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
    "сто": 100,
    "двести": 200,
    "триста": 300,
    "четыреста": 400,
    "пятьсот": 500,
    "шестьсот": 600,
    "семьсот": 700,
    "восемьсот": 800,
    "девятьсот": 900,
}

_multipliers = {
    "сотен": 100, "сотня": 100, "сотни": 100,
    "тыс": 1000, "тысяч": 1000, "тысяча": 1000, "тысячи": 1000,
    "миллион": 1000000, "миллиона": 1000000, "миллионов": 1000000,
    "миллиард": 1000000000, "миллиарда": 1000000000, "миллиардов": 1000000000,
}


def _token_is_explicit(tok):
    return re.fullmatch(r"[-+]?\d+(\.\d+)?", tok) is not None


def _ru_number_replacer(match) -> str:
    text = match.group(0)
    text = text.lower()
    # Заменяем запятые между цифрами на точку (например, 1,5 -> 1.5)
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    # Остальные точки и запятые заменяем на пробел
    text = re.sub(r"(?<!\d)[.,](?!\d)", " ", text)
    tokens = text.split()

    groups = []  # Список групп: (список токенов, тип группы)
    current_group = []
    group_type = None  # "explicit" (начинается с цифры) или "implicit" (числовое слово)
    has_multiplier = False

    # Функция для проверки, является ли токен явным числом
    def _token_is_explicit(tok):
        return re.fullmatch(r"[-+]?\d+(\.\d+)?", tok) is not None

    for token in tokens:
        # Обработка разделителя "и":
        if token == "и":
            # Если текущая группа не содержит множителя, считаем, что разделитель указывает на разрыв
            if current_group and not has_multiplier:
                groups.append((current_group, group_type))
                current_group = []
                group_type = None
                has_multiplier = False
            # Если же в группе уже есть множитель, "и" считается связующим и пропускается
            continue

        if not current_group:
            current_group = [token]
            if _token_is_explicit(token):
                group_type = "explicit"
            elif token in _number_words:
                group_type = "implicit"
            else:
                group_type = "other"
            has_multiplier = (token in _multipliers)
        else:
            if group_type == "explicit":
                if _token_is_explicit(token):
                    # Если уже встречен множитель, объединяем
                    if has_multiplier:
                        current_group.append(token)
                    else:
                        # Если текущее число <= 999, начинаем новую группу
                        try:
                            value = float(current_group[0])
                        except ValueError:
                            value = 1000
                        if value <= 999:
                            groups.append((current_group, group_type))
                            current_group = [token]
                            group_type = "explicit"
                            has_multiplier = (token in _multipliers)
                        else:
                            current_group.append(token)
                else:
                    if token in _multipliers:
                        current_group.append(token)
                        has_multiplier = True
                    elif token in _number_words:
                        try:
                            value = float(current_group[0])
                        except ValueError:
                            value = 1000
                        # Если число <= 999 и нет множителя, отделяем новое число
                        if not has_multiplier and value <= 999:
                            groups.append((current_group, group_type))
                            current_group = [token]
                            group_type = "implicit"
                            has_multiplier = False
                        else:
                            current_group.append(token)
                    else:
                        current_group.append(token)
            elif group_type == "implicit":
                if token in _number_words or token in _multipliers:
                    current_group.append(token)
                    if token in _multipliers:
                        has_multiplier = True
                elif _token_is_explicit(token):
                    groups.append((current_group, group_type))
                    current_group = [token]
                    group_type = "explicit"
                    has_multiplier = (token in _multipliers)
                else:
                    current_group.append(token)
            else:
                current_group.append(token)
                if token in _multipliers:
                    has_multiplier = True
    if current_group:
        groups.append((current_group, group_type))

    # Вычисляем значение для каждой группы по стандартной логике.
    group_values = []
    for tokens_group, _ in groups:
        total = 0.0
        current = 0.0
        for token in tokens_group:
            if token == "и":
                continue
            try:
                num = float(token)
                current += num
                continue
            except ValueError:
                pass
            if token in _number_words:
                current += _number_words[token]
            elif token in _multipliers:
                multiplier = _multipliers[token]
                if current == 0:
                    current = 1
                current *= multiplier
                total += current
                current = 0
        total += current
        group_values.append(total)

    # Если все группы содержат множитель и их несколько (например, "1 миллиард 600 миллионов"),
    # объединяем их в одно число.
    all_have_multiplier = all(any(tok in _multipliers for tok in grp) for grp, _ in groups)
    if all_have_multiplier and len(group_values) > 1:
        combined = sum(group_values)
        if combined.is_integer():
            return " " + str(int(combined)) + " "
        else:
            return " " + str(combined) + " "
    else:
        outs = []
        for val in group_values:
            if val.is_integer():
                outs.append(str(int(val)))
            else:
                outs.append(str(val))
        return " " + " ".join(outs) + " "


_all_number_words = list(_number_words) + list(_multipliers)
_prefix_trie_with_number_words = build_trie(s.lower() for s in _all_number_words)
_regex_pattern_with_number_words = trie_to_regex(_prefix_trie_with_number_words)
_re_number_words = re.compile(fr'(?:([\d., ])*\b{_regex_pattern_with_number_words}\b[и., ]*)+', flags=re.IGNORECASE)


def replace_ru_numbers(expr: str) -> str:
    expr = re.sub(r'\bминус\b', '-', expr, flags=re.IGNORECASE)
    expr = _re_number_words.sub(_ru_number_replacer, expr)
    expr = _re_denom_words.sub(_denom_words_replacer, expr)
    return expr


if __name__ == '__main__':
    # Примеры использования:
    print(replace_ru_numbers("8 сотен"))
    print(replace_ru_numbers("7 тысяч"))
    print(replace_ru_numbers("7 тыс "))
    print(replace_ru_numbers("1 миллиард, 600 миллионов"))
    print(replace_ru_numbers("1 миллиард 600 миллионов"))
    print(replace_ru_numbers("семь тысяч сто двадцать три"))

    print(replace_ru_numbers("7.1 тысяч"))
    print(replace_ru_numbers("7.123 миллионов"))
    print(replace_ru_numbers("7,123 миллионов"))

    print(replace_ru_numbers("3 пятых"))
    print(replace_ru_numbers("одна пятая"))
    print(replace_ru_numbers("пятая"))
    print(replace_ru_numbers("Две четвертых"))
    print(replace_ru_numbers("минус девять десятых"))
    print(replace_ru_numbers("пять восьмых"))
    print(replace_ru_numbers("2 пять"))
    print(replace_ru_numbers("2 тринадцать"))
    print(replace_ru_numbers("четыре и одна"))
