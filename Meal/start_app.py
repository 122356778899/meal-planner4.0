import subprocess

# 启动 Flask 应用
subprocess.Popen(['python', '1.1.py'])

# 打开默认浏览器访问应用
import webbrowser
webbrowser.open('http://127.0.0.1:8888')