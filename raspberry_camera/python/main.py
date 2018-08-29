from picamera import PiCamera
from datetime import datetime
import os, sys
from time import sleep

from lib.local_stat_raspberry import LocalStatRaspberry as LSR

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--folder", action="store", type="string", dest="folder", default="/home/pi/Desktop/images",
                      help="base folder where photos are saved")
parser.add_option("-p", "--pause", action="store", type="float", dest="pause",
                      default=1.0, help="interval between photos")
parser.add_option("-r", "--rotation", action="store", type="int", dest="rotation",
                      default=180, help="rotation of photos")
parser.add_option("-e", "--end", action="store", type="int", dest="end",
                      default=22, help="rotation of photos")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=0, help=" verbose ")

parser.add_option("--folder_local_db", action="store", type="string", dest="folder_local_db", default="/home/pi/.fotonower_config",
                      help="local folder to save stat and info")
parser.add_option("--file_local_db", action="store", type="string", dest="file_local_db", default="/home/pi/.fotonower_config/sqlite.db",
                      help="local file to save stat and info in sqlite format")

(x, args) = parser.parse_args()

folder_local_db = x.folder_local_db
file_local_db = x.file_local_db

lsr = LSR(file_local_db, folder_local_db)

camera = ""
try :
    camera = PiCamera()
    camera.start_preview()
    camera.rotation = x.rotation % 360
    print("launching script")
except Exception, e:
    print("script allready launched")
    exit(0)
folder = ""
last_hour = ""
last_minute = ""
while True:
    if x.verbose:
        sys.stdout.write(".")
        sys.stdout.flush()
    now = datetime.now()
#    now_date = str(now).replace(":", "_").replace(" ", "").replace("-", "_").replace(".", "_").replace("\/", "_")
#    print(now_date)
    day = now.strftime("%d%m%Y")
    hour = now.strftime("%H")
    minutes = now.strftime("%M")
    if int(hour) >= x.end:
        exit(0)
    if last_minute != minutes:
        folder = os.path.join(x.folder,'{}/{}/{}'.format(str(day),str(hour),str(minutes)))
        if not os.path.exists(folder):
            os.makedirs(folder)
    last_minute = minutes
    filename = folder + '/image_{}_{}_{}_{}.jpg'.format(str(day),str(hour),str(minutes),now.strftime("%S"))
    camera.capture(filename)
    lsr.append_photo(filename)
    sleep(x.pause)



