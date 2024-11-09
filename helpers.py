
import yaml
import json

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