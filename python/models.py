from PIL import Image
from PIL import ImageStat


class TakenPicture:
    def __init__(self, shutter_speed, img, config):
        self.img = img
        self.shutter_speed = shutter_speed
        self.brightness = self.calculate_brightness(img, config)
        self.delta = abs(config.ideal_brightness - self.brightness)


    def calculate_brightness(self, im_file, config):
        img = Image.open(im_file).convert('L')

        left = config.picture_left_margin + config.important_left_margin
        top = config.picture_top_margin + config.important_top_margin
        right = left + config.important_width
        bottom = top + config.important_height

        study_img = img.crop((left, top, right, bottom))
        stat = ImageStat.Stat(study_img)
        return stat.mean[0]


class PictureConfig:
    def __init__(self, shutter_speed, brightness, delta):
        self.shutter_speed = shutter_speed
        self.brightness = brightness
        self.delta = delta
