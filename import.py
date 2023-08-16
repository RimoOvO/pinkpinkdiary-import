from sqlalchemy import create_engine
from json import loads
from shutil import copyfile
from datetime import datetime
import os


db_path = r"C:\Users\Rimo\Desktop\xiaoxiaotu\dbfolder\1692174214215.db" # 导出的数据库文件
media_path = r"C:\Users\Rimo\Desktop\xiaoxiaotu\pinkimg" # 导出的图片文件夹
current_path = r"C:\Users\Rimo\Documents\Code\pinkpinkdiary-import-backup\output" # 要导入到的文件夹

# 数据库读取 & 连接
engine = create_engine("sqlite:///" + db_path, echo=True)
db = engine.connect()

# 查询所有日记
diary = db.exec_driver_sql("select _id,content,title from diary")

# 遍历日记
for i in diary:
    # 文件创建时间，默认 0
    time = 0
    with open(current_path + '\\' + i.title+'.md', "w", encoding="utf-8") as f:
        # 写入日志内容
        f.write(f"# {i.title} \n")
        f.write(i.content)

        # 查询日记的附件
        k = db.exec_driver_sql("select id,second_id,date_ymd,time_hms,attachment from main where m_type = 1 and second_id = " + str(i._id)).first()

        # 处理 DB 种的时间，将其转换为文件时间戳
        time = datetime.strptime(str(k.date_ymd) + " " + str(k.time_hms), "%Y%m%d %H:%M:%S")
        time = time.timestamp()
        time = int(time)
        
        # 如果有附件 进行如下操作
        if(k.attachment != "[]"):
            # 反序列化附件内容 json
            attachment = loads(k.attachment)

            # 遍历附件 json 
            for j in attachment:
                print(j) # 日志记录遍历时的 json

                # 获取附件文件名
                filename = j['path'].split("/")[-1]

                # 复制附件到 media 文件夹
                if not os.path.exists(current_path + "\\media"):
                    os.makedirs(current_path + "\\media")
                c = current_path + "\\media" + "\\" + str(k.date_ymd) + "-" + str(time) + '.' + filename.split(".")[-1]
                copyfile(media_path + "\\" + filename, c)
                print("succes save media file: " + c)
            
                # 在日记中插入附件
                f.write("\n![](.\media\\"+ c.split("\\")[-1] + ")")

        f.close()
    # 修改文件时间戳
    os.utime(current_path + "\\" + i.title+'.md', (time, time))