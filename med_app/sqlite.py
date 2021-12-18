from sqlite3 import Error
import sqlite3
import os
from logs import Logger


class SQLite():
    @classmethod
    def get_driver(cls, folder, file):
        return SQLite(folder, file)

    def __init__(self, path, file_name):
        self.db_file = os.path.join(path, file_name)

    def connect_db(self):
        """ establish connection with database """

        if not os.path.exists(self.db_file):
            Logger.error("database file does't exists")
            return None

        try:
            connection = sqlite3.connect(self.db_file)
            connection.execute('PRAGMA synchronous=0')

        except Error as e:
            Logger.exception(e, 'connect_db', "sdb")
            return None

        else:
            return connection

    def test_connection(self):
        """ test connection with database """
        connection = self.connect_db()
        if connection is None:
            return False

        else:
            return True

    # execute direct quaries
    def execute_select(self, query, return_dict=False):
        connection = self.connect_db()
        if connection is None:
            Logger.error("Can't read data because no connection is available")
            return None
        cursor = connection.cursor()
        try:
            # execute query
            cursor.execute(query)
            attrbs = [item[0] for item in cursor.description]

            data = cursor.fetchall()
            if return_dict:
                data = [{key: val for key, val in zip(attrbs, row)}
                        for row in data]

        except Exception as e:
            Logger.exception(e, 'execute_select', "sdb")
            Logger.info(f'query	--> {query}')
            data = None
        finally:
            cursor.close()
            connection.close()
            return data

    def execute_insert(self, query):
        connection = self.connect_db()
        if connection is None:
            Logger.error("Can't write data because no connection is available")
            return False

        flag = False
        redoFlag = False
        cursor = connection.cursor()

        try:
            cursor.execute(query)

        except Exception as e:
            Logger.exception(e, 'execute_insert', "sdb")

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag

    def execute_update(self, query):
        connection = self.connect_db()
        if connection is None:
            Logger.error(
                "Can't update data because no connection is available")
            return False

        flag = False
        cursor = connection.cursor()
        try:
            cursor.execute(query)

        except Exception as e:
            Logger.exception(e, 'execute_update', "sdb")
            Logger.info(f'query	--> {query}')
            try:
                connection.rollback()
            except Exception:
                pass

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag

    def execute(self, query):
        connection = self.connect_db()
        if connection is None:
            Logger.error(
                "Can't Execute Query Because No Connection Is Available")
            return False

        flag = False
        cursor = connection.cursor()
        try:
            cursor.execute(query)

        except Exception as e:
            Logger.exception(e, 'execute', "sdsb")
            Logger.debug(f'query	--> {query}')
            try:
                connection.rollback()
            except Exception:
                pass

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag

    def execute_transection(self, transaction):
        """ execute a transaction 
                >>> @param:transaction	-> sql quaries separated by  ';' [str] 
        """
        connection = self.connect_db()
        if connection is None:
            Logger.error(
                "Can't Execute Transaction because no connection is available")
            return False
        flag = False
        cursor = connection.cursor()
        try:
            cursor.executescript(transaction)

        except Exception as e:
            Logger.exception(e, 'execute_transection', "sdb")
            Logger.debug(f'transaction-->  {transaction}')
            try:
                connection.rollback()
            except Exception:
                pass

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag

    # with dictionary data
    def read(self, table, columns, distinct=False, where=None, orderby=None, limit=None, single=False):
        """ read data from a database table 
                >>> @param:table	-> name of table
                >>> @param:columns	-> columns to read, * to read all columns
                >>> @param:distinct	-> select distinct values 
                >>> @param:where	-> where clause for this query
                >>> @param:orderby 	-> orderby clause for this query
                >>> @param:limit	-> limit sample selection
                >>> @param:single	-> flag to get single record
        """
        connection = self.connect_db()
        if connection is None:
            Logger.error("can't read data - no connection is available")
            return None

        cursor = connection.cursor()
        data = None
        try:
            # construct query
            query = ""
            if columns == '*':
                if distinct:
                    query = f"SELECT DISTINCT * FROM {table}"
                else:
                    query = f"SELECT * FROM {table}"

            else:
                if distinct:
                    query = f"SELECT DISTINCT {', '.join(columns)} FROM {table}"
                else:
                    query = f"SELECT {', '.join(columns)} FROM {table}"

            if where is not None:
                query = query + f" WHERE {where}"

            if orderby is not None:
                query = query + f" ORDER BY {orderby}"

            if limit is not None:
                query = query + f" LIMIT {limit}"

            query += ';'
            cursor.execute(query)

            # fetch all records
            data = cursor.fetchall()
            attrbs = [item[0] for item in cursor.description]
            data = [{key: val for key, val in zip(attrbs, row)}
                    for row in data]

        except Exception as e:
            Logger.exception(e, f'read', "sdb")
            Logger.debug(f'query	--> {query}')

        finally:
            cursor.close()
            connection.close()
            if single:
                return data[0] if data and len(data) > 0 else None

            else:
                return data

    def save(self, table, data):
        """ save a dictionary into database table 
                >>> @param:table	-> name of table
                >>> @param:data		-> dict containing column name and respactive 
                                                                value. list of dict in case multiple objects
        """
        connection = self.connect_db()
        if connection is None:
            Logger.error("can't save data - no connection available")
            return False

        flag = False
        cursor = connection.cursor()
        try:
            qformat = """INSERT INTO {}({}) VALUES{};"""
            if type(data) is dict:
                if len(data.keys()) == 1:
                    query = qformat.format(table, ', '.join(
                        data.keys()), f"('{tuple(data.values())[0]}')")
                else:
                    query = qformat.format(table, ', '.join(
                        data.keys()), tuple(data.values()))

                cursor.execute(query)

            else:
                data = [{key: val for key, val in d.items() if val is not None}
                        for d in data]
                script = [qformat.format(table, ', '.join(d.keys()), tuple(d.values()))
                          for d in data]
                query = "".join(script)
                cursor.executescript(query)

        except Exception as e:
            Logger.exception(e, 'save', "sdsb")
            Logger.debug(f'query--> {query}')
            try:
                connection.rollback()
            except Exception:
                pass

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag

    def update(self, table, data, where=None):
        """ update a database table 
                >>> @param:table	-> name of table
                >>> @param:data		-> dict containing column name and respactive 
                                                                value
                >>> @param:where	-> where clause for this query
        """
        connection = self.connect_db()
        if connection is None:
            Logger.error("can't update data - no connection available")
            return False

        flag = False
        cursor = connection.cursor()
        try:
            query = f"UPDATE {table} SET "
            query += ', '.join([f" {key}='{value}' " for key,
                               value in data.items()])
            query = query if where is None else f"{query} WHERE {where}"
            cursor.execute(query)

        except Exception as e:
            Logger.exception(e, 'execute', "sdsb")
            Logger.debug(f'query--> {query}')
            try:
                connection.rollback()
            except Exception:
                pass

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag

    def remove(self, table, where):
        """ delet record from database table based on condition 
                >>> @param:table	-> name of table
                >>> @param:where	-> where clause for this query
        """
        connection = self.connect_db()
        if connection is None:
            Logger.error("can't delet record - no connection available")
            return False

        flag = False
        cursor = connection.cursor()
        try:
            query = f"DELETE FROM {table} WHERE {where}"
            cursor.execute(query)

        except Exception as e:
            Logger.exception(e, 'remove', "sdb")
            Logger.debug(f'query--> {query}')
            try:
                connection.rollback()
            except Exception:
                pass

        else:
            connection.commit()
            flag = True

        finally:
            cursor.close()
            connection.close()
            return flag
