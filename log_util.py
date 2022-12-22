#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import logging.handlers

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

log = logging.getLogger()
level = 'default'


def create_file(filename):
    path = filename[0:filename.rfind('/')]
    if not os.path.isdir(path):
        os.makedirs(path)
    if not os.path.isfile(filename):
        fd = open(filename, mode='w', encoding='utf-8')
        fd.close()
    else:
        pass


def set_handler(levels):
    if levels == 'error':
        log.addHandler(MyLog.err_handler)
    log.addHandler(MyLog.handler)


def remove_handler(levels):
    if levels == 'error':
        log.removeHandler(MyLog.err_handler)
    log.removeHandler(MyLog.handler)


def get_current_time():
    return time.strftime(MyLog.date, time.localtime(time.time()))


class MyLog:
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file = path + '/logs/log.log'
    err_file = path + '/logs/err.log'
    # log_level
    log.setLevel(LEVELS.get(level, logging.DEBUG))
    create_file(log_file)
    create_file(err_file)
    date = '%Y-%m-%d %H:%M:%S'

    handler = logging.handlers.TimedRotatingFileHandler(filename=log_file, when='D', interval=1, backupCount=0)
    err_handler = logging.handlers.TimedRotatingFileHandler(filename=err_file, when='D', interval=1, backupCount=0)

    @staticmethod
    def debug(log_meg):
        set_handler('debug')
        log.debug(f"[DEBUG] {get_current_time()} | {log_meg}")
        remove_handler('debug')

    @staticmethod
    def info(log_meg):
        set_handler('info')
        log.info(f"[INFO] {get_current_time()} | {log_meg}")
        remove_handler('info')

    @staticmethod
    def warning(log_meg):
        set_handler('warning')
        log.warning(f"[WARNING] {get_current_time()} | {log_meg}")
        remove_handler('warning')

    @staticmethod
    def error(log_meg):
        set_handler('error')
        log.error(f"[ERROR] {get_current_time()} | {log_meg}")
        remove_handler('error')

    @staticmethod
    def critical(log_meg):
        set_handler('critical')
        log.critical(f"[CRITICAL] {get_current_time()} | {log_meg}")
        remove_handler('critical')

    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    log.addHandler(console)
    console.setLevel(logging.NOTSET)


logger = MyLog

if __name__ == "__main__":
    logger.debug("This is debug message")
    logger.info("This is info message")
    logger.warning("This is warning message")
    logger.error("This is error")
    logger.critical("This is critical message")
