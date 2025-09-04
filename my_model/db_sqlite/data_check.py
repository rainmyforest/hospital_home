import sqlite3

import pandas as pd


def check_existence(database_path, table_name, conditions=None, match_all=True):
    """
    Query SQLite database for records matching conditions and return as DataFrame.

    Args:
        database_path (str): Path to the SQLite database file
        table_name (str): Name of the table to query
        conditions (dict, optional): Dictionary of column-value pairs for filtering.
                                     Defaults to None (return all records).
        match_all (bool): If True, combine conditions with AND; if False, use OR.
                          Defaults to True.

    Returns:
        pandas.DataFrame: DataFrame containing matching records (empty if no matches
                          or if table doesn't exist)

    Raises:
        sqlite3.Error: For database operation errors (except table non-existence)
    """
    # Safely escape table name to prevent SQL injection
    escaped_table_name = f'"{table_name}"'

    # Initialize query components
    where_clause = ""
    params = ()

    if conditions:
        # Escape column names and build condition placeholders
        escaped_columns = [f'"{col}"' for col in conditions.keys()]
        condition_placeholders = [f"{col} = ?" for col in escaped_columns]
        operator = " AND " if match_all else " OR "
        where_clause = f" WHERE {operator.join(condition_placeholders)}"
        params = tuple(conditions.values())

    # Construct final SQL query
    sql = f"SELECT * FROM {escaped_table_name}{where_clause}"

    # Execute query and return results
    try:
        with sqlite3.connect(database_path) as conn:
            return pd.read_sql_query(sql, conn, params=params)
    except (sqlite3.Error, pd.errors.DatabaseError):
        return pd.DataFrame()


# # 使用示例
# if __name__ == "__main__":
#     try:
#         # 示例数据
#         db_path = "example.db"
#         table = "users"
#
#         # 示例1: 检查邮箱为特定值的用户是否存在（所有条件必须匹配）
#         conditions = {"email": "zhangsan@example.com"}
#         exists = check_existence(db_path, table, conditions)
#         print(f"邮箱为 'zhangsan@example.com' 的用户存在: {exists}")
#
#         # 示例2: 检查满足任一条件的记录（使用OR逻辑）
#         conditions = {"name": "张三", "age": 25}
#         exists = check_existence(db_path, table, conditions, match_all=False)
#         print(f"姓名为 '张三' 或年龄为 25 的记录存在: {exists}")
#
#         # 示例3: 组合条件检查（所有条件必须匹配）
#         conditions = {"name": "李四", "age": 30, "email": "lisi@example.com"}
#         exists = check_existence(db_path, table, conditions)
#         print(f"姓名为 '李四'、年龄为 30 且邮箱为 'lisi@example.com' 的用户存在: {exists}")
#
#     except sqlite3.Error as e:
#         print(f"数据库错误: {e}")
#     except ValueError as e:
#         print(f"值错误: {e}")