def get_key(d: dict, value):
    res = [k for k, v in d.items() if v == value]
    if len(res) == 0:
        return None
    return res[0]
