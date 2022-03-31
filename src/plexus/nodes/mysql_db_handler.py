#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

try:
    # from plexus.nodes.message import Message
    from plexus.utils.logger import PrintLogger
    # from plexus.nodes.command import Command

except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    from src.plexus.utils.logger import PrintLogger
    # from src.plexus.nodes.message import Message
    # from src.plexus.nodes.command import Command


class MySQLdbHandler:
    """
    simple handler to save data to mysql db
    db must be installed and preconfigured before
    also exp data will be stored like this:
    db name must be experimentXX, where XX is current experiment name
    tables:
        | Tables in experimentXX |
        +------------------------+
        | debug_logs             |
        | error_logs             |
        | exp_data               |
        | experiments            |
        | fatal_logs             |
        | info_logs              |
        | raw_data               |
        | sensors                |
        | warn_logs              |
        +------------------------+

    xxx_logs is tables for different log messages

    +--------+----------------------+------+-----+-------------------+-----------------------------+
    | Field  | Type                 | Null | Key | Default           | Extra                       |
    +--------+----------------------+------+-----+-------------------+-----------------------------+
    | log_id | bigint(20) unsigned  | NO   | PRI | NULL              | auto_increment              |
    | exp_id | smallint(5) unsigned | YES  |     | NULL              |                             |
    | time   | timestamp            | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
    | level  | tinyint(4)           | YES  |     | NULL              |                             |
    | node   | varchar(100)         | YES  |     | NULL              |                             |
    | msg    | varchar(2000)        | YES  |     | NULL              |                             |
    +--------+----------------------+------+-----+-------------------+-----------------------------+


    exp_data - separate db for search experiment only

    +-----------------------+----------------------+------+-----+---------------------+-----------------------------+
    | Field                 | Type                 | Null | Key | Default             | Extra                       |
    +-----------------------+----------------------+------+-----+---------------------+-----------------------------+
    | point_id              | bigint(20) unsigned  | NO   | PRI | NULL                | auto_increment              |
    | step_id               | int(10) unsigned     | YES  |     | NULL                |                             |
    | exp_id                | smallint(5) unsigned | YES  |     | NULL                |                             |
    | red                   | int(11)              | YES  |     | NULL                |                             |
    | white                 | int(11)              | YES  |     | NULL                |                             |
    | start_time            | timestamp            | NO   |     | CURRENT_TIMESTAMP   | on update CURRENT_TIMESTAMP |
    | end_time              | timestamp            | NO   |     | 0000-00-00 00:00:00 |                             |
    | number_of_data_points | int(10) unsigned     | YES  |     | NULL                |                             |
    | point_of_calc         | double               | YES  |     | NULL                |                             |
    | f_val                 | double               | YES  |     | NULL                |                             |
    | q_val                 | double               | YES  |     | NULL                |                             |
    | is_finished           | smallint(5) unsigned | YES  |     | NULL                |                             |
    +-----------------------+----------------------+------+-----+---------------------+-----------------------------+

    raw_data is table for data from all devices:

    +-----------+----------------------+------+-----+-------------------+-----------------------------+
    | Field     | Type                 | Null | Key | Default           | Extra                       |
    +-----------+----------------------+------+-----+-------------------+-----------------------------+
    | data_id   | bigint(20) unsigned  | NO   | PRI | NULL              | auto_increment              |
    | exp_id    | smallint(5) unsigned | YES  |     | NULL              |                             |
    | time      | timestamp            | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
    | sensor_id | smallint(5) unsigned | YES  |     | NULL              |                             |
    | data      | double               | YES  |     | NULL              |                             |
    +-----------+----------------------+------+-----+-------------------+-----------------------------+


    """



    def __init__(self, db_params):
        """
        db_params is dict with params of db like
            {
            'host': 'localhost',
             'user':'admin',
             'db':'experiment',
             'password':'admin'
             }

        """
        self._db_name = "experiment" + str(self._description["experiment_number"])
        self._db_params = db_params
        self._logger = PrintLogger("")
        pass

    def _create_database(self):
        self._logger("create database")

        con = pymysql.connect(host=self._db_params["host"],
                              user=self._db_params["user"],
                              password=self._db_params["password"],
                              # db='experiment',
                              charset='utf8mb4',
                              cursorclass=pymysql.cursors.DictCursor)

        cur = con.cursor()

        cur.execute("CREATE DATABASE IF NOT EXISTS {}".format(self._db_name))
        cur.execute("use {}".format(self._db_name))

        # TODO load params from .launch and put to the database


        # create all log tables for different types of error status
        for log_table_name in ["fatal_logs", "error_logs", "warn_logs", "info_logs", "debug_logs"]:
            self._logger("create tables for all logs")
            cur.execute('create table if not exists {}'
                        ' ( log_id bigint unsigned primary key not null auto_increment,'
                        ' exp_id SMALLINT unsigned,'
                        ' time timestamp,'
                        ' level TINYINT,'
                        ' node varchar(100),'
                        ' msg varchar(2000) )'.format(log_table_name)
                        )

            cur.execute('describe {}'.format(log_table_name))
            print(cur.fetchall())

        self._logger("create table raw_data")

        cur.execute('create table if not exists raw_data'
                    ' (data_id bigint unsigned primary key not null auto_increment,'
                    ' exp_id  SMALLINT unsigned,'
                    ' time timestamp,'
                    ' sensor_id SMALLINT unsigned,'
                    ' data double)'
                    )

        cur.execute('describe raw_data')
        print(cur.fetchall())

        self._logger("create table sensors")

        cur.execute('create table if not exists sensors'
                    '(sensor_id SMALLINT unsigned primary key not null,'
                    'name varchar(100),'
                    'type varchar(100),'
                    'units varchar(100),'
                    'prec double,'
                    'description varchar(1000),'
                    'status varchar(100)'
                    ')')

        # put default data from launch file to sensors table
        self._logger("creating sensors table")
        for topic in self._raw_topics:
            # TODO add data from dict to table
            pass

        cur.execute('describe sensors')
        print(cur.fetchall())

        self._logger("create table experiments")

        cur.execute('create table if not exists experiments'
                    '( exp_id SMALLINT unsigned primary key not null,'
                    'start_date timestamp,'
                    'end_date timestamp,'
                    'params varchar(1000)'
                    ')'
                    )

        cur.execute('describe experiments')
        print(cur.fetchall())

        cur.execute('commit')
        con.close()
