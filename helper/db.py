"""
:authors: co0lc0der
:license: MIT
:copyright: (c) 2022-2023 co0lc0der
"""

import inspect
import sqlite3
import sys
import traceback
from typing import Union


class MetaSingleton(type):
    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(MetaSingleton, self).__call__(*args, **kwargs)
        return self._instances[self]


class DataBase(metaclass=MetaSingleton):
    db_name = "db.db"
    conn = None
    cursor = None

    def connect(self, db_name=""):
        if db_name != "":
            self.db_name = db_name

        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()

        return self.conn

    def c(self):
        return self.cursor


class QueryBuilder:
    _OPERATORS: list = [
        "=",
        ">",
        "<",
        ">=",
        "<=",
        "is not",
        "LIKE",
        "NOT LIKE",
        "IN",
        "NOT IN",
    ]
    _LOGICS: list = ["AND", "OR", "NOT"]
    _SORT_TYPES: list = ["ASC", "DESC"]
    _JOIN_TYPES: list = ["INNER", "LEFT OUTER", "RIGHT OUTER", "FULL OUTER", "CROSS"]
    _NO_FETCH: int = 0
    _FETCH_ONE: int = 1
    _FETCH_ALL: int = 2
    _FETCH_COLUMN: int = 3
    _conn = None
    _cur = None
    _query = None
    _sql: str = ""
    _error: bool = False
    _error_message: str = ""
    _print_errors: bool = False
    _result: Union[tuple, list] = []
    _result_dict = True
    _count: int = -1
    _params: tuple = ()

    def __init__(
        self,
        database: DataBase,
        db_name: str = "",
        result_dict: bool = True,
        print_errors: bool = False,
    ) -> None:
        self._conn = database.connect(db_name)
        self._print_errors = print_errors
        self._set_row_factory(result_dict)
        self._cur = self._conn.cursor()

    def _set_row_factory(self, result_dict: bool = True):
        self._result_dict = result_dict
        # self._conn.row_factory = sqlite3.Row
        if self._result_dict:
            self._conn.row_factory = lambda c, r: dict(
                [(col[0], r[idx]) for idx, col in enumerate(c.description)]
            )

    def query(
        self,
        sql: str = "",
        params: tuple = (),
        fetch: int = 2,
        column: Union[str, int] = 0,
    ):
        if fetch == 2:
            fetch = self._FETCH_ALL

        self.set_error()

        if sql:
            self._sql = sql

        self.add_semicolon()
        self._sql = self._sql.replace("'NULL'", "NULL")

        if params:
            self._params = params

        try:
            self._query = self._cur.execute(self._sql, self._params)

            if fetch == self._NO_FETCH:
                self._conn.commit()
            elif fetch == self._FETCH_ONE:
                self._result = self._query.fetchone()
            elif fetch == self._FETCH_ALL:
                self._result = self._query.fetchall()
            elif fetch == self._FETCH_COLUMN:
                self._result = [x[column] for x in self._query.fetchall()]

            if self._result:
                self._count = len(self._result)

            self.set_error()
        except sqlite3.Error as er:
            self._error = True
            print(f"SQL: {self._sql}")
            print(f"Params: {str(self._params)}")
            print(f'SQLite error: {" ".join(er.args)}')
            print("Exception class is: ", er.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))

        return self

    def add_semicolon(self, sql: str = "") -> str:
        new_sql = sql or self._sql

        if new_sql:
            new_sql += ";" if new_sql[-1] != ";" else ""

        if not sql:
            self._sql = new_sql

        return new_sql

    def get_sql(self) -> str:
        sql = self._sql
        if params := self._params:
            # Replace ? with markers
            for p in params:
                if isinstance(p, str):
                    sql = sql.replace("?", f"'{p}'", 1)
                else:
                    sql = sql.replace("?", str(p), 1)
        return sql

    def get_error(self) -> bool:
        return self._error

    def get_error_message(self) -> str:
        if self._print_errors and self._error:
            print(self._error_message)
        return self._error_message

    def set_error(self, message: str = "") -> None:
        self._error = bool(message)
        self._error_message = message
        if self._print_errors and self._error:
            print(self._error_message)

    def get_params(self) -> tuple:
        return self._params

    def get_result(self) -> Union[tuple, list]:
        return self._result

    def get_count(self) -> int:
        return self._count

    def reset(self) -> bool:
        self._sql = ""
        self._params = ()
        self._query = None
        self._result = []
        self._count = -1
        self.set_error()
        return True

    def all(self) -> Union[tuple, list, dict, None]:
        self.query()
        return self._result

    def one(self) -> Union[tuple, list, dict, None]:
        self.query(self._sql, self._params, self._FETCH_ONE)
        return self._result

    def go(self) -> Union[int, None]:
        self.query(self._sql, self._params, self._NO_FETCH)
        return self._cur.lastrowid

    def column(self, column: Union[str, int] = 0):
        if (self._result_dict and isinstance(column, int)) or (
            not self._result_dict and isinstance(column, str)
        ):
            self.set_error(
                f"Incorrect type of column in {inspect.stack()[0][3]} method. Result dict is {self._result_dict}"
            )
            return self

        self.query("", (), self._FETCH_COLUMN, column)
        return self._result

    def pluck(self, key: Union[str, int] = 0, column: Union[str, int] = 1):
        if (
            self._result_dict and (isinstance(key, int) or isinstance(column, int))
        ) or (
            not self._result_dict and (isinstance(key, str) or isinstance(column, str))
        ):
            self.set_error(
                f"Incorrect type of key or column in {inspect.stack()[0][3]} method. Result dict is {self._result_dict}"
            )
            return self

        self.query()
        return [(x[key], x[column]) for x in self._result]

    def count(self, table: Union[str, dict], field: str = ""):
        if not table:
            self.set_error(f"Empty table in {inspect.stack()[0][3]} method")
            return self

        if not field:
            self.select(table, "COUNT(*) AS `counter`")
        else:
            field = field.replace(".", "`.`")
            self.select(table, f"COUNT(`{field}`) AS `counter`")

        return self.one()[0]

    def get_first(self):
        return self.one()

    def get_last(self):
        self.all()
        return self._result[-1]

    def exists(self) -> bool:
        result = self.one()
        return self._count > 0

    def _prepare_aliases(
        self, items: Union[str, list, dict], as_list: bool = False
    ) -> Union[str, list]:
        if not items:
            self.set_error(f"Empty items in {inspect.stack()[0][3]} method")
            return ""

        sql = []
        if isinstance(items, str):
            sql.append(items)
        elif isinstance(items, (list, dict)):
            for item in items:
                if isinstance(items, list):
                    if isinstance(item, str):
                        sql.append(item)
                    elif isinstance(item, dict):
                        first_item = list(item.values())[0]
                        alias = list(item.keys())[0]
                        sql.append(
                            first_item
                            if isinstance(alias, int)
                            else f"{first_item} AS {alias}"
                        )
                elif isinstance(items, dict):
                    new_item = items[item]
                    sql.append(
                        new_item if isinstance(item, int) else f"{new_item} AS {item}"
                    )
        else:
            self.set_error(f"Incorrect type of items in {inspect.stack()[0][3]} method")
            return ""

        return sql if as_list else self._prepare_fieldlist(sql)

    def _prepare_conditions(self, where: Union[str, list]) -> dict:
        result = {"sql": "", "values": []}
        sql = ""

        if not where:
            return result

        if isinstance(where, str):
            sql += where
        elif isinstance(where, list):
            for cond in where:
                if isinstance(cond, list):
                    if len(cond) == 2:
                        field = self._prepare_field(cond[0])
                        value = cond[1]

                        if isinstance(value, str) and value.lower() == "is null":
                            operator = "IS NULL"
                            sql += f"({field} {operator})"
                        elif isinstance(value, str) and value.lower() == "is not null":
                            operator = "IS NOT NULL"
                            sql += f"({field} {operator})"
                        elif isinstance(value, (list, tuple)):
                            operator = "IN"
                            values = ("?," * len(value)).rstrip(",")
                            sql += f"({field} {operator} ({values}))"
                            for item in value:
                                result["values"].append(item)
                        else:
                            operator = "="
                            sql += f"({field} {operator} ?)"
                            result["values"].append(value)
                    elif len(cond) == 3:
                        field = self._prepare_field(cond[0])
                        operator = cond[1].upper()
                        value = cond[2]
                        if operator in self._OPERATORS:
                            if operator == "IN" and (isinstance(value, (list, tuple))):
                                values = ("?," * len(value)).rstrip(",")
                                sql += f"({field} {operator} ({values}))"
                                for item in value:
                                    result["values"].append(item)
                            else:
                                sql += f"({field} {operator} ?)"
                                result["values"].append(value)
                elif isinstance(cond, str):
                    upper = cond.upper()
                    if upper in self._LOGICS:
                        sql += f" {upper} "
        else:
            self.set_error(f"Incorrect type of where in {inspect.stack()[0][3]} method")
            return result

        result["sql"] = sql

        return result

    def select(self, table: Union[str, dict], fields: Union[str, list, dict] = "*"):
        if not table or not fields:
            self.set_error(f"Empty table or fields in {inspect.stack()[0][3]} method")
            return self

        self.reset()

        if isinstance(fields, (dict, list, str)):
            self._sql = f"SELECT {self._prepare_aliases(fields)}"
        else:
            self.set_error(
                f"Incorrect type of fields in {inspect.stack()[0][3]} method. Fields must be String, List or Dictionary"
            )
            return self

        if isinstance(table, (dict, str)):
            self._sql += f" FROM {self._prepare_aliases(table)}"
        else:
            self.set_error(
                f"Incorrect type of table in {inspect.stack()[0][3]} method. Table must be String or Dictionary"
            )
            return self

        return self

    def where(self, where: Union[str, list], addition: str = ""):
        if not where:
            self.set_error(f"Empty where in {inspect.stack()[0][3]} method")
            return self

        conditions = self._prepare_conditions(where)

        if addition:
            self._sql += f" WHERE {conditions['sql']} {addition}"
        else:
            self._sql += f" WHERE {conditions['sql']}"

        if isinstance(conditions["values"], list) and conditions["values"] is not []:
            self._params += tuple(conditions["values"])

        return self

    def having(self, having: Union[str, list]):
        if not having:
            self.set_error(f"Empty having in {inspect.stack()[0][3]} method")
            return self

        conditions = self._prepare_conditions(having)

        self._sql += f" HAVING {conditions['sql']}"

        if isinstance(conditions["values"], list) and conditions["values"] is not []:
            self._params += tuple(conditions["values"])

        return self

    def like(self, field: Union[str, tuple, list] = (), value: str = ""):
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return self

        if isinstance(field, str) and isinstance(value, str) and value:
            self.where([[field, "LIKE", value]])
        elif isinstance(field, str) and not value:
            self.where(field)
        elif isinstance(field, (tuple, list)):
            self.where([[field[0], "LIKE", field[1]]])

        return self

    def not_like(self, field: Union[str, tuple, list] = (), value: str = ""):
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return self

        if isinstance(field, str) and isinstance(value, str) and value:
            self.where([[field, "NOT LIKE", value]])
        elif isinstance(field, str) and not value:
            self.where(field)
        elif isinstance(field, (tuple, list)):
            self.where([[field[0], "NOT LIKE", field[1]]])

        return self

    def is_null(self, field: str = ""):
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return self
        self.where([[field, "IS NULL"]])
        return self

    def is_not_null(self, field: str):
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return self
        self.where([[field, "IS NOT NULL"]])
        return self

    def not_null(self, field: str):
        self.is_not_null(field)
        return self

    def limit(self, limit: int = 1):
        self._sql += f" LIMIT {limit}"
        return self

    def offset(self, offset: int = 0):
        self._sql += f" OFFSET {offset}"
        return self

    def _prepare_sorting(self, field: str = "", sort: str = "") -> tuple:
        if " " in field:
            splitted = field.split(" ")
            field = splitted[0]
            sort = splitted[1]

        field = self._prepare_field(field)

        sort = "ASC" if sort == "" else sort.upper()

        return field, sort

    def _prepare_field(self, field: str = "") -> str:
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return ""

        if "(" in field or ")" in field or "*" in field:
            if " AS " not in field:
                return field
            field = field.replace(" AS ", " AS `")
            return f"{field}`"
        else:
            field = field.replace(".", "`.`")
            field = field.replace(" AS ", "` AS `")
            return f"`{field}`"

    def _prepare_fieldlist(self, fields: Union[str, tuple, list] = ()) -> str:
        result = ""
        if not fields:
            self.set_error(f"Empty fields in {inspect.stack()[0][3]} method")
            return result

        if isinstance(fields, str):
            result = self._prepare_field(fields)
        elif isinstance(fields, (tuple, list)):
            fields = [self._prepare_field(field) for field in fields]
            result = ", ".join(fields)

        return result

    def order_by(self, field: Union[str, tuple, list] = (), sort: str = ""):
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return self

        if isinstance(field, str):
            field, sort = self._prepare_sorting(field, sort)

            if sort in self._SORT_TYPES:
                self._sql += f" ORDER BY {field} {sort}"
            else:
                self._sql += f" ORDER BY {field}"
        elif isinstance(field, (tuple, list)):
            new_list = []
            for item in field:
                new_item = self._prepare_sorting(item)
                new_list.append(f"{new_item[0]} {new_item[1]}")
            self._sql += " ORDER BY " + ", ".join(new_list)

        return self

    def group_by(self, field: Union[str, tuple, list] = ()):
        if not field:
            self.set_error(f"Empty field in {inspect.stack()[0][3]} method")
            return self

        self._sql += f" GROUP BY {self._prepare_fieldlist(field)}"

        return self

    def delete(self, table: Union[str, dict]):
        if not table:
            self.set_error(f"Empty table in {inspect.stack()[0][3]} method")
            return self

        if isinstance(table, (dict, str)):
            table = self._prepare_aliases(table)
        else:
            self.set_error(
                f"Incorrect type of table in {inspect.stack()[0][3]} method. Table must be String or Dictionary"
            )
            return self

        self.reset()

        self._sql = f"DELETE FROM {table}"
        return self

    def insert(self, table: Union[str, dict], fields: Union[list, dict]):
        if not table or not fields:
            self.set_error(f"Empty table or fields in {inspect.stack()[0][3]} method")
            return self

        if isinstance(table, (dict, str)):
            table = self._prepare_aliases(table)
        else:
            self.set_error(
                f"Incorrect type of table in {inspect.stack()[0][3]} method. Table must be String or Dictionary"
            )
            return self

        self.reset()

        if isinstance(fields, dict):
            values = ("?," * len(fields)).rstrip(",")
            self._sql = (
                f"INSERT INTO {table} ({self._prepare_fieldlist(list(fields.keys()))}"
                + f") VALUES ({values})"
            )
            self._params = tuple(fields.values())
        elif isinstance(fields, list):
            names = fields.pop(0)
            value = ("?," * len(names)).rstrip(",")
            v = f"({value}),"
            values = (v * len(fields)).rstrip(",")
            self._sql = (
                f"INSERT INTO {table} ({self._prepare_fieldlist(names)}"
                + f") VALUES {values}"
            )
            params = []
            for item in fields:
                if isinstance(item, list):
                    params.extend(iter(item))
            self._params = tuple(params)
        else:
            self.set_error(
                f"Incorrect type of fields in {inspect.stack()[0][3]} method. Fields must be String, List or Dictionary"
            )
            return self

        return self

    def update(self, table: Union[str, dict], fields: Union[list, dict]):
        if not table or not fields:
            self.set_error(f"Empty table or fields in {inspect.stack()[0][3]} method")
            return self

        if isinstance(table, (dict, str)):
            table = self._prepare_aliases(table)
        else:
            self.set_error(
                f"Incorrect type of table in {inspect.stack()[0][3]} method. Table must be String or Dictionary"
            )
            return self

        if isinstance(fields, (list, dict)):
            sets = "".join(f" {self._prepare_field(item)} = ?," for item in fields)
            sets = sets.rstrip(",")
        else:
            self.set_error(
                f"Incorrect type of fields in {inspect.stack()[0][3]} method. Fields must be String, List or Dictionary"
            )
            return self

        self.reset()

        self._sql = f"UPDATE {table} SET{sets}"
        self._params = tuple(fields.values())

        return self

    def join(
        self,
        table: Union[str, dict] = "",
        on: Union[str, tuple, list] = (),
        join_type: str = "INNER",
    ):
        join_type = join_type.upper()
        if not join_type or join_type not in self._JOIN_TYPES:
            self.set_error(
                f"Empty join_type or is not allowed in {inspect.stack()[0][3]} method"
            )
            return self

        if not table:
            self.set_error(f"Empty table in {inspect.stack()[0][3]} method")
            return self

        if isinstance(table, (dict, str)):
            self._sql += f" {join_type} JOIN {self._prepare_aliases(table)}"
        else:
            self.set_error(
                f"Incorrect type of table in {inspect.stack()[0][3]} method. Table must be String or Dictionary"
            )
            return self

        if on:
            if isinstance(on, (tuple, list)):
                field1 = self._prepare_field(on[0])
                field2 = self._prepare_field(on[1])
                self._sql += f" ON {field1} = {field2}"
            elif isinstance(on, str):
                self._sql += f" ON {on}"
            else:
                self.set_error(
                    f"Incorrect type of on in {inspect.stack()[0][3]} method. On must be String, Tuple or List"
                )
                return self

        self.set_error()
        return self

    def drop(self, table: str, add_exists: bool = True):
        # this method will be moved to another class
        if not table:
            self.set_error(f"Empty table in {inspect.stack()[0][3]} method")
            return self

        exists = "IF EXISTS " if add_exists else ""

        self.reset()
        self._sql = f"DROP TABLE {exists}`{table}`"

        return self

    def truncate(self, table: str):
        # this method will be moved to another class
        if not table:
            self.set_error(f"Empty table in {inspect.stack()[0][3]} method")
            return self

        self.reset()
        self._sql = f"TRUNCATE TABLE `{table}`"

        return self
