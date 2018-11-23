#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fotonower as FC
import os
import datetime
import psutil
from raspberry_camera.python.lib.local_stat_raspberry import LocalStatRaspberry as LSR

def upload(folder,day,hour,minutes,name,fc,lsr,datou):
    port_id = ""
    datou_current_id = ""
    try:
        with open(os.path.join(os.getenv('HOME'), '.fotonower_config/port_id_{}.txt'.format(day)), 'r') as f:
            port_id = f.read()
            if int(port_id) == 0:
                os.remove(os.path.join(os.getenv('HOME'), '.fotonower_config/port_id_{}.txt'.format(day)))
                print("portfolio_id is not saved in file, deleting and exiting...")
                exit(1)
        with open(os.path.join(os.getenv('HOME'), '.fotonower_config/current_id_{}.txt'.format(day)), 'w') as f:
            datou_current_id=f.read()
    except Exception as e:
        print('no port, creating one')
        port_id = str(fc.create_portfolio("{}_{}".format(name,day)))
        if int(port_id) == 0:
            print("error with portfolio, creating one with hour/min")
            port_id = str(fc.create_portfolio("{}_{}{}{}".format(name,day,hour,minutes)))
            if int(port_id) == 0:
                print("couldn't create portfolio, exiting...")
                return(1)
        with open(os.path.join(os.getenv('HOME'), '.fotonower_config/port_id_{}.txt'.format(day)),'w') as f:
            f.write(port_id)
        if datou != 0:
            ret=fc.set_datou_current(int(port_id),datou)
            try :
                datou_current_id = str(ret['id'][0])
                with open(os.path.join(os.getenv('HOME'), '.fotonower_config/current_id_{}.txt'.format(day)), 'w') as f:
                    f.write(datou_current_id)
            except:
                pass
    if int(port_id) == 0:
        print('error with portfolio, exiting...')
        exit(1)
    folder = os.path.join(folder,"{}/{}/{}".format(day,hour,minutes))
    if not os.path.exists(folder):
        print("no folder to upload.")
        return(0)
    print("uploading in " + str(port_id))
    files = [os.path.join(folder,x) for x in os.listdir(folder)]
    try :
        map_result_insert_aux,list_cur_ids = fc.upload_medias(files,portfolio_id=int(port_id) ,upload_small=True,
                                                 verbose=False, compute_classification=True, arg_aux="",auto_treatment= False,datou_current_id = datou_current_id)
        try :
            test = map_result_insert_aux.keys()
            for photo_path in test:
                lsr.upload_one(photo_path,photo_id_global=map_result_insert_aux[photo_path])
            print("uploaded " + str(len(map_result_insert_aux)) + " photos")
            print("rm")
            for photo_path in test :
                os.remove(photo_path)
                lsr.delete_one(photo_path)
            return 0
        except Exception as e:
            print("not deleting.")
            print(e)
            return -1
    except Exception as e:
        print(e)
        return -2

def reupload(day,folder,current,lsr,datou):
    if day == "":
        day = current.strftime("%d%m%Y")
    fullpath = os.path.join(folder, day)
    dict_result = {}
    uploaded = 0
    missed = 0
    for hour in os.listdir(fullpath):
        for minute in os.listdir(os.path.join(fullpath, hour)):
            res = upload(x.folder, day, hour, minute, x.name, fc,lsr,datou)
            dict_result[day + hour + minute] = res
            if res == 0:
                uploaded += 1
            else:
                missed += 1
    print("we uploaded {} folder(s) and we missed {} folder(s)".format(uploaded, missed))
    return {"uploaded": uploaded, "missed" : missed}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='uploader for rapsberry')

    parser.add_argument("-f", "--folder", action="store", type=str, dest="folder", default="/home/pi/Desktop/images",
                      help="folder where are photo to upload")
    parser.add_argument("-t", "--token", action="store", type=str, dest="token",
                      default="", help=" token ")
    parser.add_argument("-u", "--root_url", action="store", type=str, dest="root_url", default="www.fotonower.com",
                      help="root_url to upload photos")
    parser.add_argument("-d", "--datou", action="store", type=str, dest="datou",
                      default="2",help="datou id to be treated")
    parser.add_argument("-P", "--protocol", action="store", type=str, dest="protocol",
                      default="https", help="http or https")
    parser.add_argument("-n", "--port_name", action="store", type=str, dest="name",
                      default="raspberry", help="base name for portfolio")
    parser.add_argument('-j', '--job', dest="job", type=str, action="store", default="upload", help="upload or reprise")
    parser.add_argument("-D", "--day", type=str, dest='day', default="", help="day of folder to upload")
    parser.add_argument("--folder_local_db", action="store", type=str, dest="folder_local_db",
                      default="/home/pi/.fotonower_config",
                      help="local folder to save stat and info")
    parser.add_argument("--file_local_db", action="store", type=str, dest="file_local_db",
                      default="/home/pi/.fotonower_config/sqlite.db",
                      help="local file to save stat and info in sqlite format")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=0, help=" verbose ")
    parser.add_argument('--datou',action='store',dest='datou',default=0,help="datou_id to launch at upload")
    x = parser.parse_args()

    folder_local_db = x.folder_local_db
    file_local_db = x.file_local_db
    verbose = x.verbose



    lsr = None
    try:
        lsr = LSR(file_local_db, folder_local_db)
    except:
        print("no sqlite3 installed")



    def count_process(verbose = False):
        import psutil
        test = 0
        for pid in psutil.pids():
            try :
                p = psutil.Process(pid)
                cmd_line_list = p.cmdline()
                cmd_line = cmd_line_list[2] if len(cmd_line_list) >= 3 else cmd_line_list[-1] if len(cmd_line_list) > 0 else ""

                if "upload" in cmd_line:
                    test += 1

                if verbose :
                    print (str(p.cmdline()))
            except:
                pass

        print ("Count : " + str(test))

        return test



    current = datetime.datetime.now() - datetime.timedelta(minutes=1)
    print(current)
    if x.token == "" and x.job != "count" :
        print("please provide a token")
        exit(1)
    try:
        fc = FC.FotonowerConnect(x.token, x.root_url, x.protocol)
    except Exception as e:
        print("please provide a valid token")
        exit(1)
    if x.job == "count":
        count_process(verbose)
    elif x.job == "upload":
        test = count_process(verbose)

        if test > 5:
            print("too many processes, exiting")
            exit(3)
        if not os.path.isdir(x.folder):
            print("please provide a valid folder")
            exit(2)
        folder = x.folder
        day = current.strftime("%d%m%Y")
        hour = current.strftime("%H")
        minutes = current.strftime("%M")
        ret = upload(folder,day,hour,minutes,x.name,fc,lsr,x.datou)
        if ret != 0:
            print('we had an error with upload')
            if ret == 1:
                print("error is from portfolio creation or file")
            elif ret == -1:
                print("error is from upload result")
            elif ret == -1:
                print("error is from upload on API")
    elif x.job == "reprise":
        if not os.path.isdir(x.folder):
            print("please provide a valid folder")
            exit(2)
        day = x.day
        reupload(day,x.folder,current, lsr,x.datou)
    elif x.job == "test":
        print(os.getenv('PYTHONPATH'))
        from tests.upload_test import test
        ret = test(True)


