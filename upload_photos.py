#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fotonower as FC
import os
import datetime 
import shutil


def upload(folder,day,hour,minutes,name,fc):
    port_id = ""
    try:
        with open(os.path.join(os.getenv('HOME'), '.fotonower_config/port_id_{}.txt'.format(day)), 'r') as f:
            port_id = f.read()
            if int(port_id) == 0:
                os.remove(os.path.join(os.getenv('HOME'), '.fotonower_config/port_id_{}.txt'.format(day)))
                print("portfolio_id is not saved in file, deleting and exiting...")
                exit(1)
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
                                                 verbose=False, compute_classification=True, arg_aux="",auto_treatment= False)
        try :
            test = map_result_insert_aux.keys()
            print("uploaded " + str(len(map_result_insert_aux)) + " photos")
            print("rm")
            shutil.rmtree(folder)
            return 0
        except Exception as e:
            print("not deleting.")
            print(e)
            return -1
    except Exception as e:
        print(e)
        return -2

def reupload(day,folder,current):
    if day == "":
        day = current.strftime("%d%m%Y")
    fullpath = os.path.join(folder, day)
    dict_result = {}
    uploaded = 0
    missed = 0
    for hour in os.listdir(fullpath):
        for minute in os.listdir(os.path.join(fullpath, hour)):
            res = upload(x.folder, day, hour, minute, x.name, fc)
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
    x = parser.parse_args()

    current = datetime.datetime.now() - datetime.timedelta(minutes=1)
    print(current)
    if x.token == "":
        print("please provide a token")
        exit(1)
    try:
        fc = FC.FotonowerConnect(x.token, x.root_url, x.protocol)
    except Exception as e:
        print("please provide a valid token")
        exit(1)
    if x.job == "upload":
        if not os.path.isdir(x.folder):
            print("please provide a valid folder")
            exit(2)
        folder = x.folder
        day = current.strftime("%d%m%Y")
        hour = current.strftime("%H")
        minutes = current.strftime("%M")
        ret = upload(folder,day,hour,minutes,x.name,fc)
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
        reupload(day,x.folder,current)
    elif x.job == "test":
        print os.getenv('PYTHONPATH')
        from tests.upload_test import test
        ret = test(True)

