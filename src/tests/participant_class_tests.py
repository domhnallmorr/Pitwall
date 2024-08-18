import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(f"{parent_dir}\\pw_model")

from pw_model import driver_model