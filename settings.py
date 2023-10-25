import os
import psutil

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

RECEIVED_FILES = os.path.join(DIR_PATH, 'received_files')

DFS_MAIN_PATH = os.path.join(DIR_PATH, 'DFS_main')

APP_LOG = os.path.join(DFS_MAIN_PATH, 'app.log')

CLIENT_LOG = os.path.join(DIR_PATH,'Client','client.log')
# print(CLIENT_LOG)

# get the OS type mac or windows or linux
OS_TYPE = os.name

disk_usage = ''
# if os is linux or mac
if OS_TYPE == 'posix':
    disk_usage = psutil.disk_usage('/')
else:
    disk_usage = psutil.disk_usage('C:\\')
# disk_usage = psutil.disk_usage('C:\\')
FREE_SPACE = disk_usage.free
# print(FREE_SPACE)
