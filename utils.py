import logging
from pathlib import Path
import pandas as pd

# Logger
log = logging.getLogger()

def get_project_root() -> Path:
    """Return the path of the project root folder.

    Returns:
        Path: Path to project root
    """
    return Path(__file__).parent


def read_resource(file):
    """Read a resource file located in directory 'res/' in project root.
    Args:
        file (str): Filename

    Returns:
        AnyStr: The content of the resource file.
    """
    res_path = get_project_root() / 'res'
    with open(res_path / file, 'r', encoding='utf-8') as fd:
        return fd.read()


def read_csv(file, **kwargs):
    """Read csv data (located in resources folder res/csv/) into a pandas data frame.
    Args:
        file (str): Filename

    Returns:
        DataFrame: DataFrame containing the data read from the csv file
    """
    log.debug(f'Reading csv data from file "{file}" in "res/csv/"...')
    file_path = ((get_project_root() / "res") / "csv") / file
    return pd.read_csv(file_path, **kwargs)