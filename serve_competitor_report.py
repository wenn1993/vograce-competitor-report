#!/usr/bin/env python3
"""
Vograce 竞品报告本地服务器
在 localhost:8899 提供竞品分析报告访问
"""

import http.server
import socketserver
import os
from pathlib import Path

# 配置
PORT = 8899
WORKSPACE = "/Users/admin/WorkBuddy/20260324141124"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSPACE, **kwargs)

    def end_headers(self):
        # 添加CORS头支持
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_GET(self):
        """处理GET请求"""
        # 如果请求根路径，重定向到报告
        if self.path == '/' or self.path == '':
            self.path = '/vograce-competitor-report.html'
        return super().do_GET()

def main():
    """启动服务器"""
    os.chdir(WORKSPACE)

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"🚀 Vograce 竞品报告服务器已启动")
        print(f"📊 报告地址: http://localhost:{PORT}/vograce-competitor-report.html")
        print(f"📁 工作目录: {WORKSPACE}")
        print(f"⏹️  按 Ctrl+C 停止服务器")
        print("-" * 50)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
            httpd.shutdown()

if __name__ == "__main__":
    main()
