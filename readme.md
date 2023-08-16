# 粉粉日记导出脚本

> 环境要求:
> Python >= 3.6

1. 先在 APP 中导出备份至手机内，将其放入电脑中
2. 修改 import.py 的 db_path，media_path 与 current_path (对应哪些文件注释中有写，db_path 需精确到文件, media_path 与 current_path 仅需文件夹)
3. 在脚本目录下运行 `pip install -r requirements.txt`，如果你有 sqlalchemy 无需运行
4. current_path 收获成果


### 注意

仅支持导出日记的文本内容与图片，会在 md 文件中自动编写图片引入，不保证其他奇怪的格式和效果生效


> MIT License