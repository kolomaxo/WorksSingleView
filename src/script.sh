#!/bin/bash
python3 setup.py --config config.json
python3 clusterize.py --config configuration/internal_config.json --match_confidence 0.7 --data /data/works_metadata.csv
python3 api.py --config configuration/internal_config.json
