import os
import socket
from waitress import serve
from app import app

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    lan_ip = get_lan_ip()
    print("=" * 65)
    print("        INTERNHUB - OFFLINE PRODUCTION DEPLOYMENT        ")
    print("=" * 65)
    print(" WSGI Server : Waitress Production Server (Multi-threaded)")
    print(" Environment : 100% Offline (Zero Internet Dependency)")
    print("-" * 65)
    print(f" Local Access: http://127.0.0.1:{port}  or  http://localhost:{port}")
    print(f" LAN Access  : http://{lan_ip}:{port} (Other devices on your Wi-Fi)")
    print("=" * 65)
    print(" Production server is ready and serving requests...")
    serve(app, host='0.0.0.0', port=port, threads=8)
