# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
import re
import os

def parse_curl_and_save():
    # ⚠️ ，把你用 Stream 抓包复制的那一整坨💩 Curl 代码粘贴到下面三个引号中间
    raw_curl = """放在这里哦不要删除符号哦😊"""

    # --- 1. 暴力正则提取 URL ---
    # 匹配 curl 后面的第一个 http/https 链接
    url_match = re.search(r"(?i)curl\s+['\"]?(https?://[^'\"]+)['\"]?", raw_curl)
    url = url_match.group(1) if url_match else "❌ 未解析到 URL"

    # --- 2. 暴力正则提取 Cookie ---
    # 匹配 -H 'Cookie: xxxx' 里面的内容
    cookie_match = re.search(r"(?i)-H\s+['\"]?Cookie:\s*([^'\"]+)['\"]?", raw_curl)
    cookie = cookie_match.group(1) if cookie_match else "❌ 未解析到 Cookie"

    # --- 3. 暴力正则提取 User-Agent ---
    # 匹配 -H 'User-Agent: xxxx' 里面的内容
    ua_match = re.search(r"(?i)-H\s+['\"]?User-Agent:\s*([^'\"]+)['\"]?", raw_curl)
    user_agent = ua_match.group(1) if ua_match else "❌ 未解析到 User-Agent"

    # --- 4. 组装极度舒适的排版 ---
    output_text = (
        " 联通抓包数据解析成功 \n"
        "可以直接把下面的内容一段段复制到小组件脚本里了，⚠️host填写m.client.10010.com\n\n"
        "================ [ 1. URL 链接 ] ================\n"
        f"{url}\n\n"
        "================ [ 2. User-Agent ] ================\n"
        f"{user_agent}\n\n"
        "================ [ 3. Cookie (核心) ] ================\n"
        f"{cookie}\n\n"
        "=================================================\n"
    )

    # --- 5. 自动创建并保存到新文件 ---
    # 会在你的 PythonIDE 当前目录下生成这个 txt 文件
    file_name = "API提取结果.txt"
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f" 搞定！已成功帮你把数据分段提取，并存入了新文件：【{file_name}】\n")
        print(" 预览一下内容 记得还有 host 哦臭宝\n")
        print(output_text)
    except Exception as e:
        print(f"❌ 写入文件失败了: {e}")

if __name__ == "__main__":
    parse_curl_and_save()
#2026-3-20