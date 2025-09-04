import json
import sqlite3


def insert_into_table(database_path, table_name, data, id_column='id'):
    """
    向SQLite表插入数据，并将自增ID存储到指定列（如果表不存在则自动创建）

    参数:
        database_path: 数据库路径
        table_name: 目标表名
        data: 插入数据字典 {列名: 值}
        id_column: 存储ID的列名（默认为'id')

    返回:
        插入记录的自增ID

    异常:
        ValueError: 如果数据字典为空
    """
    if not data:
        raise ValueError("数据字典不能为空")

    # SQLite 类型映射
    type_mapping = {
        int: "INTEGER",
        float: "REAL",
        bool: "INTEGER",
        str: "TEXT",
        bytes: "BLOB",
        type(None): "NULL"  # 处理 None 值
    }

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        table_exists = cursor.fetchone() is not None

        # 预处理数据：将列表等非SQLite支持的类型转换为JSON字符串
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                processed_data[key] = json.dumps(value, ensure_ascii=False)  # 转换为JSON字符串
            else:
                processed_data[key] = value

        # 如果表不存在，则创建表
        if not table_exists:
            # 创建列定义（排除ID列）
            columns = []
            for key, value in processed_data.items():
                if key == id_column:
                    continue
                value_type = type(value)
                sql_type = type_mapping.get(value_type, "TEXT")  # 默认使用 TEXT
                columns.append(f"{key} {sql_type}")

            # 添加自增主键列
            if id_column:
                columns.insert(0, f"{id_column} INTEGER PRIMARY KEY AUTOINCREMENT")

            create_sql = f"""
                CREATE TABLE {table_name} (
                    {', '.join(columns)}
                )
            """
            cursor.execute(create_sql)

        # 准备插入数据（排除ID列）
        data_insert = {k: v for k, v in processed_data.items() if k != id_column}
        columns_str = ', '.join(data_insert.keys())
        placeholders = ', '.join(['?'] * len(data_insert))

        # 执行插入操作
        insert_sql = f"""
            INSERT INTO {table_name} (
                {columns_str}
            ) VALUES (
                {placeholders}
            )
        """
        cursor.execute(insert_sql, tuple(data_insert.values()))
        last_row_id = cursor.lastrowid

        # 将ID存储到指定列
        if id_column and last_row_id is not None:
            update_sql = f"""
                UPDATE {table_name} 
                SET {id_column} = ? 
                WHERE rowid = ?
            """
            cursor.execute(update_sql, (last_row_id, last_row_id))

        conn.commit()

    return last_row_id


# # 使用示例
# if __name__ == "__main__":
#     try:
#         # 示例数据
#         db_path = "example.db"
#         table = "users"
#         user_data = {
#             "name": "张三",
#             "age": 30,
#             "email": "zhangsan@example.com"
#         }
#
#         # 插入数据（表不存在时会自动创建）
#         row_id = insert_into_table(db_path, table, user_data)
#         print(f"成功插入记录，ID为: {row_id}")
#
#     except sqlite3.Error as e:
#         print(f"数据库错误: {e}")
#     except ValueError as e:
#         print(f"值错误: {e}")