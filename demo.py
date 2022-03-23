import logging
import logging.config

from create import Control
from utils import get_project_root


def setup_demo():
    """Setup demo database"""

    # Configure logging
    log_conf_path = str((get_project_root() / "conf") / "logging.conf")
    log_file_path = str((get_project_root() / "log") / "demo.log")

    logging.config.fileConfig(log_conf_path, defaults={'logfilename': log_file_path})
    log = logging.getLogger()
    log.info('Starting database setup')

    # Populate the database
    control = Control()
    control.deleteData()
    control.create_nodes()
    control.add_dashboard()
    log.info('Finished')

    # Close (file) handlers
    for handler in log.handlers:
        handler.close()
        log.removeHandler(handler)

if __name__ == '__main__':
    setup_demo()