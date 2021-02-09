import argparse
import json

def read_json_configuration():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="configuration_json", type=str, help="path to json configuration file")
    args = parser.parse_args()
    with open(args.configuration_json, 'r') as configuration_json_file:
        configuration = json.load(configuration_json_file)
    return configuration, args
