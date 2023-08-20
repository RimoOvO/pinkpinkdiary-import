from sqlalchemy import create_engine
from json import loads
from shutil import copyfile
from datetime import datetime
from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle, GENERIC_WRITE, OPEN_EXISTING
from pywintypes import Time
import time
from termcolor import colored
import os

db_path = r"F:\Cache\pinkpinkdiary-import\xiaoxiaotu\dbfolder\1692174214215.db" # 导出的数据库文件
media_path = r"F:\Cache\pinkpinkdiary-import\xiaoxiaotu\pinkimg" # 导出的图片文件夹
current_path = r"F:\Cache\pinkpinkdiary-import\output" # 要导入到的文件夹

backup_media = True # 是否备份原图 由于 db 数据 bug，有可能会导致图片丢失，所以默认开启

def log(msg, level="info"):
    if(level == "debug"):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S    ") + colored(" DEBUG " +  str(msg), "cyan"))
        return;
    if(level == "info"):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S    ") + colored(" INFO " +  str(msg)))
        return;
    if(level == "error"):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S    ") + colored(" ERROR " +  str(msg), "light_red"))
        return;
    if(level == "warn"):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S    ") + colored(" WARN " +  str(msg), "yellow"))
        return;
    if(level == "done"):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S    ") + colored(" DONE " +  str(msg), "green"))
        return;
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S    ") + colored(" [UNKNOWN LEVEL] " +  str(msg), "on_magenta"))
    
def timeOffsetAndStruct(times, format, offset):
    return time.localtime(time.mktime(time.strptime(times, format)) + offset)

# 数据库读取 & 连接
engine = create_engine("sqlite:///" + db_path, echo=True)
db = engine.connect()

# 查询所有日记
diary = db.exec_driver_sql("select _id,content,title from diary")

# 遍历日记
for i in diary:
    # 文件创建时间，默认 0
    ttime = 0
    # 创建对应文件夹
    if not os.path.exists(current_path):
        os.makedirs(current_path)
    with open(current_path + '\\' + i.title+'.md', "w", encoding="utf-8") as f:
        # 写入日志内容
        f.write(f"# {i.title} \n")
        f.write(i.content)

        # 查询日记的附件
        k = db.exec_driver_sql("select id,second_id,date_ymd,time_hms,attachment from main where m_type = 1 and second_id = " + str(i._id)).first()
        # 处理 DB 种的时间，将其转换为文件时间戳
        ttime = datetime.strptime(str(k.date_ymd) + " " + str(k.time_hms), "%Y%m%d %H:%M:%S")
        ttime = ttime.timestamp()
        ttime = int(ttime)
        
        # 如果有附件 进行如下操作
        if(k.attachment != "[]"):
            # 反序列化附件内容 json
            attachment = loads(k.attachment)
            # 附件序号
            output_media = 0
            # 遍历附件 json 
            for j in attachment:
                log(j) # 打印遍历到的 json

                # 获取附件文件名
                filename = j['path'].split("/")[-1]

                # 复制附件到 media 文件夹
                if not os.path.exists(current_path + "\\media"):
                    os.makedirs(current_path + "\\media")
                    
                c = current_path + "\\media" + "\\" + str(k.date_ymd) + str(k.time_hms).replace(':','-') + "_" + str(ttime) + '_' + str(output_media) + '.' + filename.split(".")[-1]
                # 判断文件是否重复
                if(os.path.exists(c)):
                    log("file exists: " + c, "warn")
                    c = current_path + "\\media" + "\\" + str(k.date_ymd) + str(k.time_hms).replace(':','-') + "_" + str(ttime) + '_' + str(output_media) + '_' + str(output_media) + '.' + filename.split(".")[-1]
                    
                copyfile(media_path + "\\" + filename, c)
                log("success save media file: " + c)
            
                # 在日记中插入附件
                f.write("\n![](.\media\\"+ c.split("\\")[-1] + ")")
                output_media += 1

        f.close()
    # 修改文件最后修改时间戳
    os.utime(current_path + "\\" + i.title+'.md', (ttime, ttime))
    # 判断 os 是否是 windows，用以修改文件创建时间戳
    if(os.name == "nt"):
        # 设置文件时间戳
        hFile = CreateFile(current_path + "\\" + i.title+'.md', GENERIC_WRITE, 0, None, OPEN_EXISTING, 0, 0)
        # 修改 ttime 时间戳为 YYYY-MM-DD HH:MM:SS 的格式
        ttime = Time(time.mktime(timeOffsetAndStruct(datetime.fromtimestamp(ttime).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S",0)))
        SetFileTime(hFile, ttime, ttime, ttime)
        CloseHandle(hFile)
        log("success set file ttime: " + current_path + "\\" + i.title+'.md', "info")
    else:
        # 在非 windows 系统中，不支持修改文件创建时间戳
        log("not windows os, skip set file ttime: " + current_path + "\\" + i.title+'.md', "warn")
    
    log("file output done: " + current_path + "\\" + i.title+'.md', "done")
    
# 是否备份源媒体文件夹
if(backup_media):
    if not os.path.exists(current_path + "\\media\\origin"):
                os.makedirs(current_path + "\\media\\origin")
    log("backup media file start", "info")
    for filename in os.listdir(media_path):
        copyfile(media_path + "\\" + filename, current_path + "\\media\\origin\\" + filename)
    log("backup media file done", "done")