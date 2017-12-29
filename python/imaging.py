from time import sleep
from fractions import Fraction
from datetime import datetime
import os
import json
import io
import sys
import traceback

from util import Console
from models import PictureConfig
from models import TakenPicture

path_last_config = "/pics/{0}_last_config.json"


class ImagingSystem:

    def __init__(self, camera):
        self.camera = camera
        self.last_stopped_reason = "unknown"
        self.last_count = "unknown"

    def init_camera(self):
        self.camera.iso = 100
        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = 'off'
        self.camera.exposure_mode = 'off'
        self.camera.drc_strength = 'off'
        self.camera.awb_gains = (Fraction(753, 557), Fraction(753, 557))

    def take_picture_stream(self, nb_ss):
        my_stream = io.BytesIO()
        self.camera.framerate = float(
            (float(101) - (float(nb_ss) / float(100))) / float(100))
        self.camera.shutter_speed = 1000 * nb_ss

        Console.Write("[{0}] Taking Picture ! setting={1}, ss={2}: ",datetime.today().strftime("%Y-%m-%d %H:%M:%S"), nb_ss, self.camera.shutter_speed)
        self.camera.capture(my_stream, 'jpeg')
        my_stream.seek(0)
        return my_stream

    def take_best_picture_ever(self, machine_cfg):
        machine_key = machine_cfg.display_name
        self.camera.rotation = machine_cfg.photo_rotation
        last_photoshoot = None
        if os.path.isfile(path_last_config.format(machine_key)):
            with open(path_last_config.format(machine_key), 'r') as content_file:
                j = json.loads(content_file.read())
                last_photoshoot = PictureConfig(
                    j["shutter_speed"], j["brightness"], j["delta"])

        current = None
        last = None
        checkpoint = None
        closest = None

        ss = 2 if last_photoshoot is None else last_photoshoot.shutter_speed
        self.last_count = 0
        tested_under = False
        tested_over = False
        self.last_stopped_reason = "unknown"

        while ss > 0 and ss <= machine_cfg.max_ss and self.last_count < machine_cfg.max_try and (current is None or current.delta > machine_cfg.accepted_delta):
            self.last_count += 1
            try:
                current = TakenPicture(ss, self.take_picture_stream(
                    int(ss)), machine_cfg)
                Console.WriteLine("br={0} accepted_delta={2} curr_delta={1}",
                                  current.brightness, current.delta, machine_cfg.accepted_delta)

                if current.brightness < machine_cfg.ideal_brightness:
                    Console.DebugLine("UNDER: CHECK")
                    tested_under = True

                if current.brightness > machine_cfg.ideal_brightness:
                    Console.DebugLine("OVER: CHECK")
                    tested_over = True

                if closest is None or current.delta < closest.delta:
                    Console.DebugLine("CLOSEST YET")
                    closest = current

                if current.delta < machine_cfg.accepted_delta:
                    Console.DebugLine("OK ! FINISH")
                    self.last_stopped_reason = "accepted"
                    break

                if ss == machine_cfg.max_ss and current.brightness < machine_cfg.ideal_brightness:
                    Console.DebugLine("EXPLODE")
                    self.last_stopped_reason = "max_ss"
                    break

                if ss == 1 and current.brightness > machine_cfg.ideal_brightness:
                    self.last_stopped_reason = "min_ss"
                    Console.DebugLine("DIE")
                    break

                if not tested_over:
                    checkpoint = current
                    multiplier = min(10, max(2, current.delta / 10))
                    Console.DebugLine(
                        "EXCESSIVE PUSH * {0}, CP = CUR", multiplier)
                    ss *= multiplier
                elif not tested_under:
                    checkpoint = current
                    divider = min(10, max(2, current.delta / 10))
                    Console.DebugLine(
                        "EXCESSIVE CALM DOWN / {0}, CP = CUR", divider)
                    ss /= divider
                else:
                    if ss > last.shutter_speed and current.brightness > machine_cfg.ideal_brightness:
                        Console.DebugLine("CP = LAST")
                        checkpoint = last
                    elif ss < last.shutter_speed and current.brightness < machine_cfg.ideal_brightness:
                        Console.DebugLine("CP = LAST")
                        checkpoint = last

                    pct = 100 * current.delta / \
                        (current.delta + checkpoint.delta)
                    diff_ss = abs(ss - checkpoint.shutter_speed)

                    if current.brightness > machine_cfg.ideal_brightness:
                        Console.DebugLine(
                            "CONCENTRATE BACKWARD {0:.04f}% of {1}", pct, diff_ss)
                        ss -= pct * (diff_ss) / 100
                    else:
                        Console.DebugLine(
                            "CONCENTRATE FORWARD {0:.04f}% of {1}", pct, diff_ss)
                        ss += pct * (diff_ss) / 100

                if self.last_count == machine_cfg.max_try:
                    Console.DebugLine("ENOUGH")
                    self.last_stopped_reason = "max_tries"
                    break

                if ss > machine_cfg.max_ss:
                    Console.DebugLine("JUST BELOW EXPLOSION")
                    ss = machine_cfg.max_ss

                if ss < 1:
                    Console.DebugLine("JUST ABOVE DEATH")
                    ss = 1

                if int(ss) == int(current.shutter_speed):
                    self.last_stopped_reason = "closest"
                    break

                last = current
                current = None

            except Exception as inst:
                Console.WriteLine("")
                print("Unexpected error:", sys.exc_info()[0])
                print(type(inst))    # the exception instance
                print(inst.args)     # arguments stored in .args
                print(inst)
                traceback.print_exc()
                break

        current.img.seek(0)

        cfg = open(path_last_config.format(machine_key), "w")
        cfg.write(json.dumps(
            {
                'shutter_speed': current.shutter_speed,
                'brightness': current.brightness,
                'delta': current.delta,
                'stopped_reason': self.last_stopped_reason
            }, sort_keys=True, indent=4, separators=(',', ': ')))
        cfg.close()

        return current
