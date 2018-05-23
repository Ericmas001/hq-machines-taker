#!/usr/bin/python

import subprocess
from datetime import datetime
import sys
from picamera import PiCamera
import io
from PIL import Image
import json
import os
import traceback
import requests

from util import Console
from configs import HqConfig, AppConfig
from imaging import ImagingSystem

path_full_photo = "{0}{1}_{2}_{3:04d}_{4:02d}_{5}.jpg"
path_cropped = "{0}{1}_{2}.jpg"
url_ws = "http://wash.ericmas001.com"
config_path = "/etc/hq_machines_taker.cfg"

def take_best_picture_remembering(app_cfg, system, machine_cfg):
    machine_key = machine_cfg.display_name

    Console.WriteLine("-------------------------------------------------")

    Console.WriteLine("[{0}] Taking the best pic ever for {1} ({2})",
                      datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                      machine_key,
                      machine_cfg.name)

    current = system.take_best_picture_ever(machine_cfg)

    takenTime = datetime.today()
    filename = takenTime.strftime("%Y-%m-%d_%H.%M.%S")
    path_final = path_cropped.format(app_cfg.root_path, machine_key.lower(), filename)

    Console.WriteLine("[{0}] Finished because {1}: {2}",
                      datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                      system.last_stopped_reason,
                      path_final)

    if machine_cfg.must_save_full_pic:
        full_image_path = path_full_photo.format(app_cfg.root_path,
                                                 machine_key,
                                                 filename,
                                                 int(current.shutter_speed),
                                                 system.last_count,
                                                 system.last_stopped_reason)
        open(full_image_path, 'wb').write(current.img.read())
        Console.WriteLine("saved")
        current.img.seek(0)
    img = Image.open(current.img)
    img.crop((
        machine_cfg.picture_left_margin,
        machine_cfg.picture_top_margin,
        machine_cfg.picture_left_margin + machine_cfg.picture_width,
        machine_cfg.picture_top_margin + machine_cfg.picture_height
    )).save(path_final)
    url = url_ws + '/api/upload'
    files = {"form_input_field_name1": open(path_final, "rb")}
    requests.post(url, files=files)

    hqurl = "{0}/api/machines/picture/upload".format(app_cfg.url_hq)
    headers = {
        "HqTakerName": app_cfg.taker_name,
        "HqApiKey": app_cfg.api_key,
        "HqIdMachine": str(machine_cfg.id),
        "HqTakenTime": takenTime.strftime("%Y-%m-%d %H:%M:%S"),
    }
    files = {"form_input_field_name1": open(path_final, "rb")}
    requests.post(hqurl, files=files, headers=headers)
    os.remove(path_final)

def get_config(app_cfg):
    Console.WriteLine("[{0}] Get config from WS",
                      datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    hqurl = "{0}/api/machines/config/list/{1}/{2}".format(app_cfg.url_hq, app_cfg.taker_name, app_cfg.api_key)
    hq_cfg = requests.get(hqurl).json()
    return HqConfig(hq_cfg)

Console.WriteLine("")
Console.WriteLine("#######################################################")
Console.WriteLine("#######################################################")
app_config = None
try:
    with open(config_path, 'r') as content_file:
        j = json.loads(content_file.read())
        app_config = AppConfig(j)

    Console.WriteLine("[{0}] Taking control of camera",
                      datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    camera = PiCamera(resolution=(2592, 1944))
    try:
        system = ImagingSystem(camera, app_config)
        Console.WriteLine("[{0}] Init camera parameters",
                          datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        system.init_camera()

        while True:
            try:
                Console.WriteLine("=======================================================")

                hq_config = get_config(app_config)

                Console.WriteLine("[{0}] {1} ({2}) has {3} machines to stalk: [{4}]",
                          datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
                          hq_config.display_name.encode('utf-8'),
                          hq_config.name,
                          len(hq_config.machines),
                          ", ".join([m.display_name for m in hq_config.machines]))

                for machine_cfg in hq_config.machines:
                    take_best_picture_remembering(app_config, system, machine_cfg)

                pass

            except Exception as inst:
                Console.WriteLine("")
                print("Unexpected error:", sys.exc_info()[0])
                print(type(inst))    # the exception instance
                print(inst.args)     # arguments stored in .args
                print(inst)
                traceback.print_exc()

        pass

    except Exception as inst:
        Console.WriteLine("")
        print("Unexpected error:", sys.exc_info()[0])
        print(type(inst))    # the exception instance
        print(inst.args)     # arguments stored in .args
        print(inst)
        traceback.print_exc()
    finally:
        camera.close()
except Exception as inst:
    Console.WriteLine(">>>>>   C A M E R A    I S    B U S Y   <<<<<")
