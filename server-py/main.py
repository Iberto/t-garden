import socket
import logging
from os import mkdir, path
from sys import exc_info, getsizeof
from traceback import extract_tb
import json
import pandas as pd
from datetime import datetime

UDP_SERVER_PORT = 4040
UDP_SERVER_IP = "0.0.0.0"

LOG_FOLDERNAME = 'log'
LOG_FILENAME = 'log.log'
LOG_FILEMODE = 'a'
LOG_FORMAT = '%(asctime)-15s %(levelname)-8s - %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = logging.DEBUG

# folder to store log file
if not path.exists(LOG_FOLDERNAME):
    mkdir(LOG_FOLDERNAME)

# check exists dataframe otherwise create it.
if not path.isfile('dataframe.csv'):
    df = pd.DataFrame(columns=['datetime', 'plant', 'temperature', 'air-humidity', 'soil-humidity'])
    df.set_index('datetime', inplace=True)
    df.index = pd.to_datetime(df.index)
    df.to_csv('dataframe.csv')
    del df

# basicConfig set the root logger
logging.basicConfig(filename=LOG_FOLDERNAME+'/'+LOG_FILENAME, filemode=LOG_FILEMODE,
                    format=LOG_FORMAT, datefmt=LOG_DATEFMT, level=LOG_LEVEL)


def _extract_exception_function():
    # get function that threw the exception
    trace = exc_info()[-1]
    stack = extract_tb(trace, 1)
    function_name = stack[0][2]
    return function_name


def udp_server_set_up():
    _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    _s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        _pair = (UDP_SERVER_IP, UDP_SERVER_PORT)
        _s.bind(_pair)

    except socket.error as _e:
        # obsolete -> is similar to OSError
        logging.error("@" + _extract_exception_function() + " - Socket.error: " + str(_e))
        _s.close()
        _s = None
    except OSError as _e:
        # this could happen due to an incorrect ip address
        logging.error("@" + _extract_exception_function() + " - OSError: " + str(_e))
        _s.close()
        _s = None
    except OverflowError as _e:
        # this could happen due to an incorrect port number
        logging.error("@" + _extract_exception_function() + " - OverflowError: " + str(_e))
        _s.close()
        _s = None

    return _s


def udp_server_run(s):
    while True:
        try:
            _data, _client = s.recvfrom(4*1024)
            yield _data, _client
        except Exception as _e:
            logging.warning("@" + _extract_exception_function() + " - " + str(_e))


def data_handler(data):
    json_data = json.loads(data)
    json_data['datetime'] = str(datetime.now())
    dfj = pd.DataFrame([json_data], columns=['datetime', 'plant', 'temperature', 'air-humidity', 'soil-humidity'])
    dfj.set_index('datetime', inplace=True)
    dfj.index = pd.to_datetime(dfj.index)
    dfj.to_csv("dataframe.csv", mode='a', header=False)


def main():
    s = udp_server_set_up()
    if s is None:
        exit(0)
    else:
        for data, client in udp_server_run(s):
            bsize = getsizeof(data)
            logging.info("Received " + str(bsize) + " Bytes from " + client[0] + ":" + str(client[1]))
            data_handler(data)


if __name__ == '__main__':
    main()
