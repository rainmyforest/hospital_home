from my_data.user_data import pages_json


def base_converter(value: str, from_base: int, to_base: int, i: int = len(pages_json.DEFAULT_PAGES)) -> str:
    """
    将任意进制的字符串转换为另一种进制的字符串

    参数:
    value (str): 输入的数值字符串
    from_base (int): 输入数值的进制
    to_base (int): 目标进制
    i (int): 输出字符串的最小长度（左侧补零），默认为0表示不补零

    返回:
    str: 转换后的数值字符串（左侧补零到指定长度）

    异常:
    ValueError: 如果输入值包含非法字符或进制超出范围
    """
    # 验证进制范围
    if not 2 <= from_base <= 36 or not 2 <= to_base <= 36:
        raise ValueError("进制必须在2-36之间")

    # 检查空输入
    if not value:
        raise ValueError("输入值不能为空")

    if value[0] == "-":
        return ''

    # 定义可用字符集
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    value = value.upper()  # 统一转为大写处理

    # ====== 第一步：从原进制转换为十进制 ======
    decimal_value = 0
    for char in value:
        if char not in digits:
            raise ValueError(f"字符 '{char}' 不是有效的数字字符")
        digit = digits.index(char)
        if digit >= from_base:
            raise ValueError(f"字符 '{char}' 不符合 {from_base} 进制")
        decimal_value = decimal_value * from_base + digit

    # ====== 第二步：从十进制转换为目标进制 ======
    # 处理零值情况
    if decimal_value == 0:
        result = "0"
    # 十进制直接返回
    elif to_base == 10:
        result = str(decimal_value)
    # 转换为其他进制
    else:
        result = ""
        temp = decimal_value
        while temp > 0:
            remainder = temp % to_base
            result = digits[remainder] + result
            temp //= to_base

    # ====== 第三步：长度处理（左侧补零） ======
    # 计算需要补充的零的数量
    zeros_to_add = max(0, i - len(result))
    # 补充前导零
    result = '0' * zeros_to_add + result

    return result

# # 测试示例
# test_cases = [
#     ("33212", 4, 10),  # 输出: 335
#     ("FF", 16, 2),  # 输出: 11111111
#     ("-101", 2, 10),  # 输出: -5
#     ("0", 10, 2),  # 输出: 0
#     ("-0", 10, 2),  # 输出: 0
#     ("10", 10, 16),  # 输出: A
#     ("1A", 16, 10),  # 输出: 26
#     ("ZZ", 36, 10),  # 输出: 1295
#     ("-ZZ", 36, 10),  # 输出: -1295
# ]
#
# for value, from_base, to_base in test_cases:
#     try:
#         print(f"base_converter({value!r}, {from_base}, {to_base}) = {base_converter(value, from_base, to_base)!r}")
#     except ValueError as e:
#         print(f"转换错误: {e}")
