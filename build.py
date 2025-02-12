import PyInstaller.__main__
import os

# 确保在脚本所在目录运行
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PyInstaller.__main__.run([
    'douyin_gui.py',  # 主程序文件
    '--name=抖音视频下载器',  # 生成的exe名称
    '--windowed',  # 使用GUI模式，不显示控制台
    '--onefile',  # 打包成单个exe文件
    '--icon=icon.ico',  # 如果你有图标的话
    '--add-data=README.md;.',  # 添加额外文件
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不询问确认
    '--hidden-import=requests',  # 添加隐式依赖
    '--hidden-import=PyQt5',
]) 