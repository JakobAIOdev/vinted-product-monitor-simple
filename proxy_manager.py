import random
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ProxyManager:
    def __init__(self, proxy_file="proxies.txt"):
        self.proxy_file = Path(proxy_file)
        self.proxies = self.load_proxies()

    def load_proxies(self):
        if not self.proxy_file.exists():
            print(f"{Colors.YELLOW}[WARN] File: {self.proxy_file} not found!{Colors.END}")
            return []
        
        raw_list = []
        with open(self.proxy_file, 'r') as f:
            raw_list = [line.strip() for line in f if line.strip()]

        formatted = []
        for raw in raw_list:
            formatted_url = self.format_proxy(raw)
            if formatted_url:
                formatted.append(formatted_url)
        
        print(f"{Colors.BLUE}[INFO] File: {len(formatted)} Proxies loaded{Colors.END}")

        return formatted
    
    def format_proxy(self, proxy_str):
        if proxy_str.startswith("http"):
            return proxy_str
        
        parts = proxy_str.split(":")

        try:
            user = parts[-2]
            password = parts[-1]
            port = parts[-3]
            
            host_parts = parts[:-3]
            host = ":".join(host_parts)
            
            if ":" in host:
                return f"http://{user}:{password}@[{host}]:{port}"
            else:
                return f"http://{user}:{password}@{host}:{port}"
                
        except Exception:
            return None

    def get_proxy(self):
        if not self.proxies:
            return None
        
        url = random.choice(self.proxies)
        return {"http": url, "https": url}
