import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from socket import error as SocketError

import requests


USER_AGENT = "ClashforWindows/0.19.21"
SCHEME_PATTERN = re.compile(r"https?://", re.IGNORECASE)
URL_CHAR_PATTERN = re.compile(r"[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]")
TRAILING_CHARS = ",.;:!?)]}>'\"，。；：！？】）〉》、"
LEADING_CHARS = "<([{\"'【（〈《"
EXPORT_DIR = Path.cwd()


def format_size(num_bytes: int) -> str:
    negative = num_bytes < 0
    size = float(abs(num_bytes))
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            text = f"{size:.2f}{unit}"
            return f"-{text}" if negative else text
        size /= 1024
    return "0.00B"


def parse_subscription_userinfo(header_value: str) -> Dict[str, int]:
    result: Dict[str, int] = {}
    matches = re.findall(r"([A-Za-z]+)=(\d+)", header_value)
    for key, value in matches:
        result[key.lower()] = int(value)
    return result


def format_remaining_seconds(seconds: int) -> str:
    if seconds < 0:
        seconds = abs(seconds)
        prefix = "已过期"
    else:
        prefix = "距离到期还有"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if days > 0:
        return f"{prefix}{days}天{hours}小时{minutes}分{secs}秒"
    if hours > 0:
        return f"{prefix}{hours}小时{minutes}分{secs}秒"
    if minutes > 0:
        return f"{prefix}{minutes}分{secs}秒"
    return f"{prefix}{secs}秒"


def clean_candidate_url(url: str) -> str:
    url = url.strip().strip(LEADING_CHARS).rstrip(TRAILING_CHARS)
    while url and url[-1] in TRAILING_CHARS:
        url = url[:-1]
    return url


def looks_like_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def extract_urls(text: str) -> List[str]:
    result: List[str] = []
    seen = set()
    starts = [m.start() for m in SCHEME_PATTERN.finditer(text)]

    for i, start in enumerate(starts):
        next_start = starts[i + 1] if i + 1 < len(starts) else len(text)
        end = start

        while end < len(text):
            if end > start and end < next_start and text[end:end + 7].lower() == "http://":
                break
            if end > start and end < next_start and text[end:end + 8].lower() == "https://":
                break
            if end >= next_start:
                break
            if not URL_CHAR_PATTERN.match(text[end]):
                break
            end += 1

        raw = text[start:end]
        url = clean_candidate_url(raw)
        if not url or not looks_like_http_url(url):
            continue
        if url not in seen:
            seen.add(url)
            result.append(url)

    stripped = clean_candidate_url(text.strip())
    if not result and looks_like_http_url(stripped):
        result.append(stripped)

    return result


def export_positive_urls(urls: List[str], base_dir: Optional[Path] = None) -> Optional[Path]:
    if not urls:
        return None

    output_dir = Path(base_dir) if base_dir else EXPORT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"positive_sub_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path.write_text("\n".join(urls) + "\n", encoding="utf-8")
    return file_path


def query_sub_info(url: str, timeout: int = 12) -> Dict[str, object]:
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    sub_header: Optional[str] = response.headers.get("Subscription-Userinfo")
    if not sub_header:
        raise ValueError("未获取到 Subscription-Userinfo，可能该订阅不提供流量或到期信息。")

    info = parse_subscription_userinfo(sub_header)
    upload = info.get("upload", 0)
    download = info.get("download", 0)
    total = info.get("total", 0)
    expire = info.get("expire")

    used = upload + download
    remain = total - used

    result: Dict[str, object] = {
        "订阅链接": url,
        "总流量": format_size(total) if total else "未知",
        "剩余流量": format_size(remain) if total else "未知",
        "已上传": format_size(upload),
        "已下载": format_size(download),
        "到期时间": "未知",
        "到期说明": "可能是无限期订阅，或服务端未返回 expire",
        "剩余流量字节": remain,
        "查询成功": True,
    }

    if expire:
        expire_dt = datetime.fromtimestamp(expire).astimezone()
        now_ts = int(datetime.now().astimezone().timestamp())
        result["到期时间"] = expire_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        result["到期说明"] = format_remaining_seconds(expire - now_ts)

    return result


def render_success_block(data: Dict[str, object], index: int, total_count: int) -> str:
    return (
        f"[{index}/{total_count}] 查询成功\n"
        f"订阅链接: {data['订阅链接']}\n"
        f"总流量:   {data['总流量']}\n"
        f"剩余流量: {data['剩余流量']}\n"
        f"已上传:   {data['已上传']}\n"
        f"已下载:   {data['已下载']}\n"
        f"到期时间: {data['到期时间']}\n"
        f"说明:     {data['到期说明']}\n"
    )


def render_error_block(url: str, error_message: str, index: int, total_count: int) -> str:
    return (
        f"[{index}/{total_count}] 查询失败\n"
        f"订阅链接: {url}\n"
        f"错误信息: {error_message}\n"
    )


def run_batch_query(raw_text: str) -> Dict[str, object]:
    raw_text = raw_text.strip()
    if not raw_text:
        return {"ok": False, "message": "请先输入或粘贴内容。"}

    urls = extract_urls(raw_text)
    if not urls:
        return {"ok": False, "message": "未识别到可查询的 http/https 链接。"}

    results: List[str] = []
    success_count = 0
    positive_urls: List[str] = []

    for index, url in enumerate(urls, start=1):
        try:
            data = query_sub_info(url)
            results.append(render_success_block(data, index, len(urls)))
            success_count += 1
            remain_bytes = int(data.get("剩余流量字节", 0))
            if remain_bytes > 0 and str(data["订阅链接"]) not in positive_urls:
                positive_urls.append(str(data["订阅链接"]))
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "未知"
            results.append(render_error_block(url, f"HTTP 请求失败，状态码: {status_code}", index, len(urls)))
        except requests.RequestException as exc:
            results.append(render_error_block(url, f"网络请求失败: {exc}", index, len(urls)))
        except Exception as exc:
            results.append(render_error_block(url, f"查询失败: {exc}", index, len(urls)))

    export_text = ("\n".join(positive_urls) + "\n") if positive_urls else ""
    export_path = export_positive_urls(positive_urls)
    summary_lines = [
        f"共识别 {len(urls)} 个链接，成功 {success_count} 个，失败 {len(urls) - success_count} 个。",
        f"剩余流量大于 0 的可用链接：{len(positive_urls)} 个。",
    ]
    if export_path:
        summary_lines.append(f"已同时保存到脚本目录: {export_path.name}")
    else:
        summary_lines.append("没有可导出的可用链接。")

    summary = "\n".join(summary_lines) + f"\n{'=' * 72}\n\n"
    final_text = summary + (f"\n{'-' * 72}\n\n".join(results) if results else "没有可显示的结果。\n")
    return {
        "ok": True,
        "urls": urls,
        "success_count": success_count,
        "total_count": len(urls),
        "positive_count": len(positive_urls),
        "export_path": str(export_path) if export_path else "",
        "export_name": export_path.name if export_path else "",
        "export_text": export_text,
        "positive_urls": positive_urls,
        "text": final_text,
    }


HTML_PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>订阅查询工具</title>
<style>
:root{
  --bg1:#0f172a;--bg2:#111827;--card:#ffffff;--text:#111827;--muted:#6b7280;
  --primary:#2563eb;--primary2:#1d4ed8;--line:#e5e7eb;--ok:#16a34a;--warn:#dc2626;
}
*{box-sizing:border-box}
body{
  margin:0;padding:18px;background:linear-gradient(180deg,var(--bg1),var(--bg2));
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
  color:var(--text);min-height:100vh;
}
.wrap{max-width:980px;margin:0 auto}
.card{
  background:var(--card);border-radius:18px;padding:16px;margin:0 0 14px;
  box-shadow:0 10px 30px rgba(0,0,0,.16)
}
.hero{color:#fff;background:linear-gradient(135deg,#1d4ed8,#7c3aed)}
h1{margin:0 0 8px;font-size:24px}
p{margin:8px 0;line-height:1.7}
.small{font-size:13px;opacity:.9}
textarea{
  width:100%;min-height:220px;border:1px solid var(--line);border-radius:14px;padding:14px;
  font-size:14px;line-height:1.6;resize:vertical;outline:none
}
textarea:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(37,99,235,.12)}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
button,a.linkbtn{
  border:0;background:linear-gradient(135deg,var(--primary),var(--primary2));color:#fff;
  padding:11px 16px;border-radius:12px;font-size:14px;text-decoration:none;cursor:pointer
}
button.secondary{background:#6b7280}
button.ghost{background:#eef2ff;color:#1e3a8a}
.status{margin-top:12px;font-size:14px;color:var(--muted)}
.status.ok{color:var(--ok)}
.status.warn{color:var(--warn)}
pre{
  margin:0;white-space:pre-wrap;word-break:break-word;background:#0b1220;color:#e5e7eb;
  padding:14px;border-radius:14px;min-height:260px;overflow:auto;font-size:13px;line-height:1.65
}
.meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
.badge{background:#f3f4f6;border-radius:999px;padding:8px 12px;font-size:13px;color:#374151}
.note{background:#eff6ff;color:#1e3a8a;border-radius:12px;padding:12px 14px;font-size:13px;line-height:1.6;margin-top:12px}
.export{margin-top:12px;display:none}
.exportbox{
  width:100%;min-height:120px;border:1px solid var(--line);border-radius:14px;padding:12px;
  font-size:13px;line-height:1.6;background:#f8fafc;color:#0f172a
}
code{background:rgba(255,255,255,.18);padding:2px 6px;border-radius:6px}
</style>
</head>
<body>
<div class="wrap">
  <div class="card hero">
    <h1>订阅链接查询</h1
    <p class="small">支持：单链接查询、混杂文本自动提取、多链接批量查询、页面内直接导出可用链接。</p>
  </div>

  <div class="card">
    <textarea id="input" placeholder="把订阅链接，或者包含很多文字/历史结果的整段内容粘贴到这里"></textarea>
    <div class="actions">
      <button onclick="runQuery()">开始查询</button>
      <button class="secondary" onclick="clearAll()">清空</button>
      <button class="ghost" onclick="copyResult()">复制结果</button>
      <button class="ghost" onclick="fillDemo()">填入示例</button>
    </div>
    <div id="status" class="status">就绪</div>
    <div class="meta">
      <div class="badge">自动识别 http / https</div>
      <div class="badge">页面内导出 + 一键复制</div>
    </div>
    <div class="note">
      小提示：查询完成后，可用链接会直接显示在页面下方，可一键复制。
    </div>
  </div>

  <div class="card">
    <pre id="output">结果会显示在这里。</pre>
  </div>

  <div class="card export" id="exportBox">
    <div style="font-weight:700;margin-bottom:10px">可用订阅链接（剩余流量大于 0）</div>
    <textarea id="exportText" class="exportbox" readonly placeholder="查询完成后，这里会显示可复制的导出内容"></textarea>
    <div class="actions">
      <button onclick="copyExport()">复制可用链接</button>
      <button class="ghost" onclick="downloadExport()">浏览器内下载 txt</button>
    </div>
    <div id="exportHint" class="status">还没有导出内容</div>
  </div>
</div>
<script>
let lastExportText = '';
let lastExportName = '';

function setStatus(text, cls=''){
  const el = document.getElementById('status');
  el.textContent = text;
  el.className = 'status' + (cls ? ' ' + cls : '');
}

function setExportHint(text, cls=''){
  const el = document.getElementById('exportHint');
  el.textContent = text;
  el.className = 'status' + (cls ? ' ' + cls : '');
}

async function runQuery(){
  const input = document.getElementById('input').value.trim();
  const output = document.getElementById('output');
  const exportBox = document.getElementById('exportBox');
  const exportText = document.getElementById('exportText');
  exportBox.style.display = 'none';
  exportText.value = '';
  lastExportText = '';
  lastExportName = '';

  if(!input){
    setStatus('请先输入或粘贴内容。', 'warn');
    return;
  }

  setStatus('正在查询，请稍候…');
  output.textContent = '正在查询…';
  setExportHint('还没有导出内容');

  try{
    const res = await fetch('/query', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({text: input})
    });
    const data = await res.json();

    if(!data.ok){
      setStatus(data.message || '查询失败', 'warn');
      output.textContent = data.message || '查询失败';
      return;
    }

    output.textContent = data.text || '';
    setStatus(`查询完成：成功 ${data.success_count}/${data.total_count}，可用 ${data.positive_count} 个`, 'ok');

    if(data.export_text){
      lastExportText = data.export_text;
      lastExportName = data.export_name || ('positive_sub_urls_' + Date.now() + '.txt');
      exportText.value = data.export_text;
      exportBox.style.display = 'block';
      setExportHint(`已生成 ${data.positive_count} 个可用链接，可直接复制；同时已保存到脚本目录：${data.export_name || 'txt 文件'}`, 'ok');
    }
  }catch(err){
    setStatus('请求失败：' + err, 'warn');
    output.textContent = '请求失败：' + err;
  }
}

function clearAll(){
  document.getElementById('input').value = '';
  document.getElementById('output').textContent = '结果会显示在这里。';
  document.getElementById('exportBox').style.display = 'none';
  document.getElementById('exportText').value = '';
  lastExportText = '';
  lastExportName = '';
  setStatus('已清空');
}

async function copyResult(){
  const text = document.getElementById('output').textContent || '';
  try{
    await navigator.clipboard.writeText(text);
    setStatus('结果已复制到剪贴板', 'ok');
  }catch(err){
    setStatus('复制失败：' + err, 'warn');
  }
}

async function copyExport(){
  if(!lastExportText){
    setExportHint('没有可复制的导出内容', 'warn');
    return;
  }
  try{
    await navigator.clipboard.writeText(lastExportText);
    setExportHint('可用链接已复制到剪贴板', 'ok');
  }catch(err){
    setExportHint('复制失败：' + err, 'warn');
  }
}

function downloadExport(){
  if(!lastExportText){
    setExportHint('没有可下载的导出内容', 'warn');
    return;
  }
  try{
    const blob = new Blob([lastExportText], {type:'text/plain;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = lastExportName || ('positive_sub_urls_' + Date.now() + '.txt');
    document.body.appendChild(a);
    a.click();
    a.remove();
    setExportHint('已触发浏览器内下载；若环境不支持，请直接点“复制可用链接”', 'ok');
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }catch(err){
    setExportHint('下载触发失败：' + err + '，请直接复制可用链接', 'warn');
  }
}

function fillDemo(){
  document.getElementById('input').value =
`这里有一段混杂文本：\nhttps://example.com/api/v1/client/subscribe?token=abc123\n\n这是历史结果粘贴：订阅链接：https://demo.example.org/sub?token=xyz789剩余时间：145天3小时`;
  setStatus('已填入示例，可直接点开始查询');
}
</script>
</body>
</html>
"""


class WebHandler(BaseHTTPRequestHandler):
    def _set_common_headers(self, content_type: str, content_length: int, status: int = 200, extra_headers: Optional[Dict[str, str]] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()

    def _safe_write(self, data: bytes) -> None:
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, SocketError):
            return

    def _send_json(self, payload: Dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._set_common_headers("application/json; charset=utf-8", len(data), status)
        self._safe_write(data)

    def do_OPTIONS(self) -> None:
        self._set_common_headers("text/plain; charset=utf-8", 0, 204)

    def do_GET(self) -> None:
        if self.path == "/":
            body = HTML_PAGE.encode("utf-8")
            self._set_common_headers("text/html; charset=utf-8", len(body), 200)
            self._safe_write(body)
            return

        if self.path.startswith("/download/"):
            filename = self.path.split("/download/", 1)[1]
            if not filename:
                self._send_json({"ok": False, "message": "文件名无效"}, status=400)
                return
            file_path = EXPORT_DIR / Path(filename).name
            if not file_path.exists() or not file_path.is_file():
                self._send_json({"ok": False, "message": "文件不存在"}, status=404)
                return
            data = file_path.read_bytes()
            headers = {"Content-Disposition": f'attachment; filename="{file_path.name}"'}
            self._set_common_headers("text/plain; charset=utf-8", len(data), 200, headers)
            self._safe_write(data)
            return

        self._send_json({"ok": False, "message": "Not Found"}, status=404)

    def do_POST(self) -> None:
        if self.path != "/query":
            self._send_json({"ok": False, "message": "Not Found"}, status=404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw) if raw else {}
            text = str(data.get("text", ""))
            result = run_batch_query(text)
            self._send_json(result)
        except Exception as exc:
            self._send_json({"ok": False, "message": f"服务端处理失败: {exc}"}, status=500)

    def log_message(self, format: str, *args) -> None:
        return


def try_open_browser(url: str) -> None:
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


def run_web_mode() -> None:
    host = "127.0.0.1"
    server = None
    port = 8765
    for candidate in [8765, 8766, 8767, 8080, 8000]:
        try:
            server = ThreadingHTTPServer((host, candidate), WebHandler)
            port = candidate
            break
        except OSError:
            continue

    if server is None:
        raise RuntimeError("无法启动本地网页服务，请检查端口占用情况。")

    url = f"http://{host}:{port}/"
    print("启动成功：HTML 查询界面已就绪")
    print(f"请在浏览器或应用内网页预览打开：{url}")
    print("按停止运行即可结束服务。")
    try_open_browser(url)
    server.serve_forever()


if __name__ == "__main__":
    run_web_mode()
