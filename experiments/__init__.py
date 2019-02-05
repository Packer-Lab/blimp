import os
_base_path = os.path.dirname(__file__)
_experiment_files = [f.split('.')[0] for f in os.listdir(_base_path) if 'init' not in f]

for _experiment_file in _experiment_files:
    exec('from experiments.{} import *'.format(_experiment_file))
