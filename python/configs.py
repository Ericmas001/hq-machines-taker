class HqConfig:

    def __init__(self, config):
        self.name = config["TakerName"]
        self.display_name = config["TakerDisplayName"]
        self.machines = [HqMachineConfig(cfg) for cfg in config["Machines"]]

class HqMachineConfig:
    machine_key = "MachineConfig"
    taker_key = "TakerConfig"

    def __init__(self, config):
        self.id = config["IdMachine"]
        self.name = config["MachineName"]
        self.display_name = config["MachineDisplayName"]

        self.picture_width = int(config[HqMachineConfig.machine_key]["PictureWidth"])
        self.picture_height = int(config[HqMachineConfig.machine_key]["PictureHeight"])
        self.important_left_margin = int(config[HqMachineConfig.machine_key]["ImportantLeftMargin"])
        self.important_top_margin = int(config[HqMachineConfig.machine_key]["ImportantTopMargin"])
        self.important_width = int(config[HqMachineConfig.machine_key]["ImportantWidth"])
        self.important_height = int(config[HqMachineConfig.machine_key]["ImportantHeight"])

        self.must_save_full_pic = eval(config[HqMachineConfig.taker_key]["SaveFullPic"])
        self.ideal_brightness = int(config[HqMachineConfig.taker_key]["IdealBrightness"])
        self.max_try = int(config[HqMachineConfig.taker_key]["MaxTry"])
        self.accepted_delta = float(config[HqMachineConfig.taker_key]["AcceptedDelta"])
        self.picture_left_margin = int(config[HqMachineConfig.taker_key]["PictureLeftMargin"])
        self.picture_top_margin = float(config[HqMachineConfig.taker_key]["PictureTopMargin"])
        self.photo_rotation = int(config[HqMachineConfig.taker_key]["PhotoRotation"])
        self.max_ss = float(config[HqMachineConfig.taker_key]["MaxSS"])