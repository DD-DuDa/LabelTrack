import yaml

def load_yaml(path):
    with open(path) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg

class configs():
    def __init__(self, config_path):
        self.config = load_yaml(config_path)
        self.source = self.config['source']
        self.save_result = self.config['save_result']
        self.fp16 = self.config['fp16']
        self.experiment_name = self.config['experiment_name']
        self.name = self.config['name']
        self.exp_file = self.config['exp_file']
        self.ckpt = self.config['ckpt']
        self.device = self.config['device']
        self.fps = self.config['fps']
        self.track_thresh = self.config['track_thresh']
        self.track_buffer = self.config['track_buffer']
        self.match_thresh = self.config['match_thresh']
        self.aspect_ratio_thresh = self.config['aspect_ratio_thresh']
        self.min_box_area = self.config['min_box_area']
        self.mot20 = self.config['mot20']