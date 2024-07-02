__all__ = ['text_conversion']


def _calculate_lt_w(s: str = ""):

    s = s.strip()

    if not s:
        return 0

    mapping = {
        "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
        "十": 10, "百": 100, "千": 1000,
        "两": 2
    }

    need = {"十", "百", "千"}

    skip = {"零"}

    # 二十， 一百零一，两千零二十
    if len(s) == 1:
        return mapping[s[0]]

    if len(s) == 2:
        # 零一
        if s[0] not in need and s[1] not in need:
            return mapping[s[0]] + mapping[s[1]]
        elif s[0] not in need and s[1] in need:
            return mapping[s[0]] * mapping[s[1]]
        else:
            raise ValueError("This conversion is not currently supported")

    result = 0
    first_num = 1
    # 九千三百零一
    for i, v in enumerate(s):

        # Encountered 0, skipping
        if v in skip:
            continue

        if i != len(s) - 1:
            if s[i] not in need and s[i+1] in need:
                first_num = mapping[v]
                continue

            if s[i] in need:
                result += first_num * mapping[v]
        else:
            if s[i] in need:
                result += first_num * mapping[v]
            else:
                result += mapping[v]

            return result


def _calculate_lt_1yi(s: str = "") -> int:

    s = s.strip()

    if not s:
        return 0

    border = "万"
    border_v = 10000

    if border in s:
        v = s.split(border)
        result = _calculate_lt_w(v[0]) * border_v + _calculate_lt_w(v[1])
        return result
    else:
        return _calculate_lt_w(s)


def text_conversion(s: str) -> int:
    """
    文本转换, 一百 -> 100, 九千九十九 -> 9099
    :param s:
    :return:
    """
    return _calculate_lt_1yi(s)
