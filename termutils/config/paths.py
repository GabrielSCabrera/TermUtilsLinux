from pathlib import Path

from termutils.config import defaults

# Main storage directory in `Home/`
# package_data = Path.home() / defaults.data_directory

# User-Accessible data storage directory in 'Home/Documents/'
output_data = Path.home() / 'Documents' / defaults.outputs_directory

# If necessary, creates the above directories on module initialization
# package_data.mkdir(exist_ok = True)
output_data.mkdir(exist_ok = True)
