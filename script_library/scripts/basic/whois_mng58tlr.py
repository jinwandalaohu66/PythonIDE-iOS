import socket
import re
from datetime import datetime, timedelta, timezone


def get_tld(domain):
    parts = domain.strip().lower().split(".")
    if len(parts) < 2:
        return ""
    return parts[-1]


def normalize_domain(domain):
    domain = domain.strip()
    if not domain:
        return ""

    if "://" in domain:
        domain = domain.split("://", 1)[1]
    domain = domain.split("/", 1)[0]
    domain = domain.split("@", 1)[-1]

    if domain.startswith("[") and "]" in domain:
        return ""
    if ":" in domain:
        host, port = domain.rsplit(":", 1)
        if re.fullmatch(r"\d+", port):
            domain = host
        else:
            return ""

    domain = domain.strip().strip(".").lower()
    if not domain:
        return ""

    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        return ""

    if "." not in domain or ".." in domain or len(domain) > 253:
        return ""

    labels = domain.split(".")
    for label in labels:
        if not label or len(label) > 63:
            return ""
        if label.startswith("-") or label.endswith("-"):
            return ""
        if not re.fullmatch(r"[a-z0-9-]+", label):
            return ""
        if re.fullmatch(r"\d+", label):
            return ""

    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", domain):
        return ""

    return domain


def query_whois_server(server, domain):
    with socket.create_connection((server, 43), timeout=10) as sock:
        sock.sendall((domain + "\r\n").encode("utf-8"))
        chunks = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks).decode("utf-8", errors="replace")


def find_whois_server(domain):
    iana_response = query_whois_server("whois.iana.org", domain)
    refer_server = ""
    for line in iana_response.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "whois" and value:
            return value
        if key == "refer" and value:
            refer_server = value
    return refer_server


def parse_whois_text(text):
    data = {}
    dns_list = []
    status_list = []

    field_map = {
        "domain name": "domain",
        "domain": "domain",
        "registrar": "registrar",
        "sponsoring registrar": "registrar",
        "registrar organization": "registrar",
        "creation date": "creation_date",
        "created": "creation_date",
        "created on": "creation_date",
        "registered on": "creation_date",
        "registration time": "creation_date",
        "registration date": "creation_date",
        "registry expiry date": "expiry_date",
        "expiration date": "expiry_date",
        "expiry date": "expiry_date",
        "expire": "expiry_date",
        "expires on": "expiry_date",
        "expiration time": "expiry_date",
        "paid-till": "expiry_date",
        "renewal date": "expiry_date",
        "updated date": "updated_date",
        "last updated on": "updated_date",
        "last modified": "updated_date",
        "changed": "updated_date",
        "updated date time": "updated_date",
        "modification time": "updated_date",
        "registrar iana id": "iana_id",
        "iana id": "iana_id",
        "iana_id": "iana_id",
    }

    status_keys = {"status", "domain status"}
    dns_keys = {"name server", "nserver", "nserver1", "nserver2", "nserver3", "nserver4"}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if not value:
            continue

        mapped_key = field_map.get(key)
        if mapped_key:
            if mapped_key == "domain":
                data[mapped_key] = value.lower()
            elif mapped_key not in data:
                data[mapped_key] = value
            continue

        if key in status_keys:
            status_value = value.split()[0].strip().lower()
            if status_value and status_value not in status_list:
                status_list.append(status_value)
            continue

        if key in dns_keys:
            dns_value = value.split()[0].strip(".").lower()
            if dns_value and dns_value not in dns_list:
                dns_list.append(dns_value)
            continue

        if key == "dnssec" and "dnssec" not in data:
            data["dnssec"] = value

    data["status_list"] = status_list
    data["dns_list"] = dns_list
    return data


def parse_datetime(value):
    value = value.strip()
    if not value:
        return None

    iso_value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_value)
    except ValueError:
        pass

    iso_value = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", iso_value)
    try:
        return datetime.fromisoformat(iso_value)
    except ValueError:
        pass

    normalized_value = re.sub(r"\s+UTC$", " +0000", value, flags=re.IGNORECASE)
    normalized_value = re.sub(r"\s+GMT$", " +0000", normalized_value, flags=re.IGNORECASE)

    patterns = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d-%b-%Y %H:%M:%S",
        "%Y.%m.%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y-%m-%d %H:%M:%S %z",
        "%Y.%m.%d %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a %b %d %H:%M:%S %Y",
    ]

    for pattern in patterns:
        try:
            return datetime.strptime(normalized_value, pattern)
        except ValueError:
            pass
    return None


def format_datetime_to_utc8(value):
    dt = parse_datetime(value)
    if not dt:
        return value
    utc8 = timezone(timedelta(hours=8))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(utc8)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC+8")


def translate_status(status):
    status_map = {
        "ok": "正常",
        "inactive": "未激活",
        "active": "已激活",
        "clientdeleteprohibited": "客户端禁止删除",
        "clienthold": "客户端暂停解析",
        "clientrenewprohibited": "客户端禁止续费",
        "clienttransferprohibited": "客户端禁止转移",
        "clientupdateprohibited": "客户端禁止更新",
        "pendingcreate": "创建处理中",
        "pendingdelete": "删除处理中",
        "pendingrenew": "续费处理中",
        "pendingrestore": "恢复处理中",
        "pendingtransfer": "转移处理中",
        "pendingupdate": "更新处理中",
        "serverdeleteprohibited": "注册局禁止删除",
        "serverhold": "注册局暂停解析",
        "serverrenewprohibited": "注册局禁止续费",
        "servertransferprohibited": "注册局禁止转移",
        "serverupdateprohibited": "注册局禁止更新",
    }
    return status_map.get(status.strip().lower(), status)


def get_domain_age_text(creation_date_str):
    dt = parse_datetime(creation_date_str)
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    years = int((now - dt).days / 365.2425)
    if years > 0:
        return f"{years}年老米"
    return ""


def normalize_dnssec(value):
    text = value.strip().lower()
    if not text or text in ("unsigned", "unsigned delegation", "no", "false", "inactive"):
        return "未配置"
    if text in ("signed", "yes", "true", "active"):
        return "已配置"
    return value


def print_row(label, value):
    print(f"{label}: {value}")


def get_whois_server(domain):
    whois_server = find_whois_server(domain)
    if whois_server:
        return whois_server

    tld = get_tld(domain)
    if not tld:
        return ""

    return f"whois.nic.{tld}"


def main():
    domain = input("请输入你的域名: ").strip()
    if not domain:
        print("域名格式无效")
        return

    domain = normalize_domain(domain)
    if not domain:
        print("域名格式无效")
        return

    try:
        whois_server = get_whois_server(domain)
        if not whois_server:
            print("无法识别域名后缀")
            return

        result = query_whois_server(whois_server, domain)
        info = parse_whois_text(result)

        display_domain = info.get("domain", domain)
        age_text = get_domain_age_text(info.get("creation_date", ""))
        if age_text:
            print_row("域名", f"{display_domain} {age_text}")
        else:
            print_row("域名", display_domain)

        print_row("注册商", info.get("registrar", "未知"))

        creation_date = info.get("creation_date")
        expiry_date = info.get("expiry_date")
        updated_date = info.get("updated_date")

        print_row("注册日", format_datetime_to_utc8(creation_date) if creation_date else "未知")
        print_row("过期日", format_datetime_to_utc8(expiry_date) if expiry_date else "未知")

        if updated_date:
            print_row("更新日", format_datetime_to_utc8(updated_date))

        if info.get("iana_id"):
            print_row("IANA_ID", info["iana_id"])

        if info.get("status_list"):
            print_row("状态", " ".join(translate_status(s) for s in info["status_list"]))
        else:
            print_row("状态", "未知")

        if info.get("dns_list"):
            print_row("DNS", " ".join(info["dns_list"]))
        else:
            print_row("DNS", "未知")

        print_row("DNSSEC", normalize_dnssec(info.get("dnssec", "未配置")))
    except Exception as e:
        print(f"查询失败: {e}")


if __name__ == "__main__":
    main()