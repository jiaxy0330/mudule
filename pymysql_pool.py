#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import pymysql
from dbutils.pooled_db import PooledDB

# from conf.conf import base_path
# from core.service import parse_yaml

# from common.db.mysql_config import MysqlConfig

"""
    pymysql封装总结
    https://blog.csdn.net/zhj_1121/article/details/121070412

    python操作mysql之只看这篇就够了
    https://www.jianshu.com/p/4e72faebd27f

    关于PooledDB使用autocommit的方法
    https://blog.51cto.com/abyss/1736844
"""


class MysqlPool(object):
    """
    MySQL 数据库连接池类 配置变量
    """

    '''
        :param
        reset: how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)

        :param 
        setsession: optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
    '''

    '''
        https://blog.51cto.com/abyss/1736844
        其中的
        setsession=['SET AUTOCOMMIT = 1']
        就是用来设置线程池是否打开自动更新的配置，0为False，1为True
    '''

    # 初始化数据库连接池变量
    __pool = None

    # 创建连接池的最大数量
    __MAX_CONNECTIONS = 1
    # 连接池中空闲连接的初始数量
    __MIN_CACHED = 1
    # 连接池中空闲连接的最大数量
    __MAX_CACHED = 1
    # 共享连接的最大数量
    __MAX_SHARED = 1

    # 超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
    __BLOCK = True
    # 单个连接的最大重复使用次数
    __MAX_USAGE = 100

    # 当返回到池时，连接应该如何重置
    # (False或None回滚以begin()开始的事务，为了安全起见，总是发出回滚)
    __RESET = True
    # 设置自动提交
    __SET_SESSION = ['SET AUTOCOMMIT = 1']

    # 不能是 UTF-8
    __CHARSET = 'UTF8'

    def __init__(self, host, port, user, password, database):
        """
        :param host: 数据库主机地址
        :param port: 端口号
        :param user: 用户名
        :param password: 密码
        :param database: 数据库名
        """
        if not self.__pool:
            # self代表当前类的实例，即为 MysqlPool（） 带小括号，执行后的数据。
            # __class__，魔法函数，代表从当前类的实例中，获取当前类，即为 MysqlPool 不带小括号的类。
            # __pool，这个代表的事类的变量，即为在类下面创建的初始化连接池，__pool
            self.__class__.__pool = PooledDB(
                creator=pymysql,
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,

                maxconnections=self.__MAX_CONNECTIONS,
                mincached=self.__MIN_CACHED,
                maxcached=self.__MAX_CACHED,
                maxshared=self.__MAX_SHARED,

                blocking=self.__BLOCK,
                maxusage=self.__MAX_USAGE,
                setsession=self.__SET_SESSION,
                reset=self.__RESET,

                charset=self.__CHARSET,
                ping=4

            )

    def get_connect(self):
        return self.__pool.connection()


class MysqlCursor(object):
    """
    从数据库配置环境，取出数据库配置参数
    这里的参数，可以不从外部导入，直接手动写入也可以。
    """

    # host = MysqlConfig().current_config()[0]
    # port = MysqlConfig().current_config()[1]
    # user = MysqlConfig().current_config()[2]
    # password = MysqlConfig().current_config()[3]
    # database = MysqlConfig().current_config()[4]

    def __init__(self, db_config) -> None:
        """
        :param host: 数据库主机地址
        :param port: 端口号
        :param user: 用户名
        :param password: 密码
        :param database: 数据库名
        """
        self.__host = db_config.get('host')
        self.__port = db_config.get("port")
        self.__user = db_config.get('user')
        self.__password = db_config.get('password')
        self.__database = db_config.get('db')
        # self.__cursor = self.getCursor()

        # 初始化数据库连接池
        self.connects_pool = MysqlPool(
            host=self.__host,
            port=self.__port,
            user=self.__user,
            password=self.__password,
            database=self.__database
        )
        # self.__conn = self.connects_pool.get_connect()

    def __enter__(self):
        """
        # with 上下文管理，魔法函数，进入with时调用
        :return: 当前类
        """
        # 从数据库链接池，获取一个数据库链接
        connect = self.connects_pool.get_connect()
        # 从获取的数据库链接，获取一个光标
        # cursor = connect.cursor(pymysql.cursors.DictCursor)
        cursor = connect.cursor()

        '''
        # https://blog.51cto.com/abyss/1736844
        # 如果使用连接池 则不能在取出后设置 而应该在创建线程池时设置
        # connect.autocommit = False 
        '''
        # 将数据库链接，赋值给当前类，方便__exit__函数调用
        self._connect = connect
        # 将数据库光标，赋值给当前类，方便__exit__函数调用
        self._cursor = cursor

        # __enter__函数，必须返回当前类
        return self

    def __exit__(self, *exc_info):
        """
        # with 上下文管理，魔法函数，退出with时调用
        :param exc_info: 异常信息，元祖
        :return: None
        """
        # 退出with上下文时，使用当前类链接，提交数据库语句
        self._connect.commit()
        # 关闭光标
        self._cursor.close()
        # 关闭链接
        self._connect.close()

    # def getCursor(self):
    #     cursor = self.__conn.cursor()
    #     return cursor

    @property
    def cursor(self):
        """
        数据库连接池，取出链接，取出光标，转换为光标属性
        :return: 数据库连接池的光标
        """
        return self._cursor

    def get_one(self, sql, args=None):
        try:
            self.cursor.execute(sql, args)
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"get_one_error:{e}")
            return False

# if __name__ == "__main__":
#     db_config = parse_yaml(f'dev.storage', base_path + "/conf/db_config.yaml")
#     with MysqlCursor(db_config) as sqlManager:
#         # 获取数据库的方法
#         sql = f"select count(1) from {db_config.get('table')} " \
#               "where create_time>= '2022-11-28 00:00:00' and create_time<'2022-11-28 23:59:59'"
#         data = sqlManager.get_one(sql)
#         # db.cursor.execute("select count(id) as total from people")
#         # data = db.cursor.fetchone()
#         print('--------统计数据条数', data)
