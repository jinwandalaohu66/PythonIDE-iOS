import base64
import secrets
import hmac
import hashlib
import struct
import time
import urllib.parse


def generate_base32_secret(byte_length=20):
    random_bytes = secrets.token_bytes(byte_length)
    secret = base64.b32encode(random_bytes).decode("utf-8")
    return secret.rstrip("=")


def build_otpauth_uri(secret, account_name, issuer_name):
    label = issuer_name + ":" + account_name

    params = {
        "secret": secret,
        "issuer": issuer_name,
        "algorithm": "SHA1",
        "digits": "6",
        "period": "30"
    }

    uri = "otpauth://totp/" + urllib.parse.quote(label)
    uri += "?" + urllib.parse.urlencode(params)
    return uri


def base32_decode_no_padding(secret):
    secret = secret.strip().replace(" ", "").upper()
    missing_padding = len(secret) % 8

    if missing_padding:
        secret += "=" * (8 - missing_padding)

    return base64.b32decode(secret)


def generate_totp(secret, interval=30, digits=6):
    key = base32_decode_no_padding(secret)
    counter = int(time.time() // interval)
    counter_bytes = struct.pack(">Q", counter)

    hmac_hash = hmac.new(
        key,
        counter_bytes,
        hashlib.sha1
    ).digest()

    offset = hmac_hash[-1] & 0x0F

    code_int = struct.unpack(">I", hmac_hash[offset:offset + 4])[0]
    code_int = code_int & 0x7FFFFFFF

    code = code_int % (10 ** digits)
    return str(code).zfill(digits)


def verify_totp(secret, user_code, interval=30, digits=6, window=1):
    current_time = int(time.time())
    key = base32_decode_no_padding(secret)

    for offset in range(-window, window + 1):
        test_time = current_time + offset * interval
        counter = int(test_time // interval)
        counter_bytes = struct.pack(">Q", counter)

        hmac_hash = hmac.new(
            key,
            counter_bytes,
            hashlib.sha1
        ).digest()

        dynamic_offset = hmac_hash[-1] & 0x0F

        code_int = struct.unpack(">I", hmac_hash[dynamic_offset:dynamic_offset + 4])[0]
        code_int = code_int & 0x7FFFFFFF

        expected_code = str(code_int % (10 ** digits)).zfill(digits)

        if expected_code == user_code:
            return True

    return False


def main():
    print("======================================")
    print(" Google Authenticator 密钥生成器")
    print(" 手机 Python IDE 纯 Python 版")
    print("======================================")

    issuer_name = input("请输入服务名称，例如 MyApp：").strip()
    account_name = input("请输入账号名称，例如 ding@example.com：").strip()

    if issuer_name == "":
        issuer_name = "MyApp"

    if account_name == "":
        account_name = "user@example.com"

    secret = generate_base32_secret()
    uri = build_otpauth_uri(secret, account_name, issuer_name)

    print("")
    print("生成完成：")
    print("--------------------------------------")
    print("服务名称：", issuer_name)
    print("账号名称：", account_name)
    print("TOTP 密钥：")
    print(secret)
    print("--------------------------------------")
    print("Google Authenticator 链接：")
    print(uri)
    print("--------------------------------------")

    print("")
    print("使用方法：")
    print("1. 打开 Google Authenticator")
    print("2. 选择添加代码")
    print("3. 选择输入设置密钥")
    print("4. 账号名称填写上面的账号名称")
    print("5. 密钥填写上面的 TOTP 密钥")
    print("6. 密钥类型选择基于时间")

    current_code = generate_totp(secret)
    print("")
    print("当前这台设备根据密钥算出的 6 位验证码是：")
    print(current_code)
    print("这个数字应该和 Google Authenticator 里显示的数字一致。")

    while True:
        print("")
        user_code = input("输入 Google Authenticator 当前显示的 6 位验证码测试，直接回车退出：").strip()

        if user_code == "":
            print("已退出。请妥善保存密钥。")
            break

        if not user_code.isdigit() or len(user_code) != 6:
            print("请输入 6 位数字。")
            continue

        if verify_totp(secret, user_code):
            print("验证成功，这个密钥可以正常使用。")
            break
        else:
            print("验证失败。请检查手机时间是否准确，或等待下一个 30 秒验证码。")

    print("")
    print("重要提醒：")
    print("TOTP 密钥不要发给别人。")
    print("谁拿到密钥，谁就能生成同样的验证码。")


main()