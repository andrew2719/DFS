import os
import psutil

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

RECEIVED_FILES = os.path.join(DIR_PATH, 'received_files')

DFS_MAIN_PATH = os.path.join(DIR_PATH, 'DFS_main')

APP_LOG = os.path.join(DFS_MAIN_PATH, 'app.log')


disk_usage = psutil.disk_usage('C:\\')
FREE_SPACE = disk_usage.free
