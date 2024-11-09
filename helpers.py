
import yaml
import json
import base64

def read_config(config_path =  'config.yaml'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config
    
def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8")as fp:
        json.dump(data, fp)


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8")as fp:
        return json.load(fp)
    

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def generator_simulator(content: str):
    for token in content.split(" "):
        yield token + " "