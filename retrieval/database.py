#!/usr/bin/env python3

import os
import psycopg2
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Database:
    database_connection = None

    def __init__(self):
        """
        Initializes the database connection.
        """
        if self.database_connection is None:
            self.__init_database__()

    @classmethod
    def __init_database__(cls):
        cls.database_connection = psycopg2.connect(
            host     = os.environ['POSTGRES_HOST'],
            port     = os.environ['POSTGRES_PORT'],
            database = os.environ['POSTGRES_DB'],
            user     = os.environ['POSTGRES_TOOL_USER'],
            password = os.environ['POSTGRES_TOOL_PASSWORD'],
        )
        return cls.database_connection

    def db_execute(self, query: str, data: tuple) -> list[tuple]:
        """
        Execute the query with data.

        :param query: SQL query to execute.
        :param data: Data to pass to the query.
        :return: List of tuples containing the results of the query.
        """
        try:
            with self.database_connection:
                with self.database_connection.cursor() as curs:
                    curs.execute(query, data)
                    return curs.fetchall()
        except psycopg2.InterfaceError as e:
            # connection already closed ?
            # Reinitialize connection and try again
            self.__init_database__()
            with self.database_connection:
                with self.database_connection.cursor() as curs:
                    curs.execute(query, data)
                    return curs.fetchall()





if __name__ == "__main__":
    # Test the module
    pass
