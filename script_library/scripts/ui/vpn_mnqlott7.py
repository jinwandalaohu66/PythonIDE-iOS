import requests
import base64
from urllib.parse import quote

def fetch_and_generate_vmess():
    data = requests.get("https://fastconn.github.io/v/servers.json").json()
    
    u = data["cfgs"]["vmess"]["a"]["u"]
    pt = data["cfgs"]["vmess"]["a"]["pt"]
    
    for item in data["l"]:
        for server in item.get("servers", []) + item.get("vip-bak", []):
            if server.get("ip") and server.get("city"):
                vmess_b64 = base64.b64encode(f"auto:{u}@{server['ip']}:{pt}".encode()).decode()
                print(f"vmess://{vmess_b64}?remarks={quote(server['city'])}&allowInsecure=1&alterId=1")

if __name__ == "__main__":
    fetch_and_generate_vmess()