import re
def check_id_card(id_str):
    if len(id_str) != 18 : return False
    last = id_str[17].upper()
    if not (last.isdigit() or last == 'X') : return False
    try:
        if not re.search(r"^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$",id_str).group():pass
    except:
        return False
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    total = sum(int(id_str[i]) * weights[i] for i in range(17))
    mod = total % 11
    expected = codes[mod]
    return last == expected
if __name__  ==  "__main__":
    print(check_id_card(input("输入18位完整sfz号码：")))