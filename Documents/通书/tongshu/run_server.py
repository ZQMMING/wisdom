"""TONGSHU Server — 启动入口"""
import sys, os

# 项目根目录（run_server.py 所在目录）
ROOT = os.path.dirname(os.path.abspath(__file__))

# 添加包路径（calendar 优先，避免 tongshu 包名解析错误）
for pkg in reversed(["tongshu-calendar", "tongshu-bazi", "tongshu-server"]):
    p = os.path.normpath(os.path.join(ROOT, "packages", pkg))
    if p not in sys.path:
        sys.path.insert(0, p)

from tongshu_server.server.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")