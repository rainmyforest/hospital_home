import sqlite3
from typing import Dict, Any, List


def smart_update_record_by_id(db_path: str, table_name: str, record_id: int, data_dict: Dict[str, Any]) -> bool:
    """
    智能更新SQLite数据库中的记录，自动处理列是否存在的情况

    参数:
        db_path (str): SQLite数据库文件路径
        table_name (str): 要更新的表名
        record_id (int): 要更新的记录ID
        data_dict (Dict[str, Any]): 包含字段名和值的字典，用于更新记录

    返回:
        bool: 更新成功返回True，失败返回False
    """
    if not data_dict:
        print("警告: 数据字典为空，无需更新")
        return False

    # 验证表名和列名安全性
    if not is_valid_sql_identifier(table_name):
        print(f"错误: 表名 '{table_name}' 包含非法字符")
        return False

    for column in data_dict.keys():
        if not is_valid_sql_identifier(column):
            print(f"错误: 列名 '{column}' 包含非法字符")
            return False

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. 检查记录是否存在
        if not record_exists(cursor, table_name, record_id):
            print(f"错误: ID {record_id} 的记录不存在")
            return False

        # 2. 获取表的列信息
        existing_columns = get_table_columns(cursor, table_name)
        if not existing_columns:
            print(f"错误: 表 '{table_name}' 不存在或无法访问")
            return False

        # 3. 添加不存在的列
        columns_to_add = [col for col in data_dict.keys()
                          if col not in existing_columns and col != "id"]

        for column in columns_to_add:
            value = data_dict[column]
            col_type = infer_sql_type(value)
            if not add_column_to_table(cursor, table_name, column, col_type):
                print(f"添加列 {column} 失败，更新操作中止")
                conn.rollback()
                return False

        # 4. 构建更新语句(只更新data_dict中提供的字段)
        set_clause, params = prepare_update_statement(data_dict, record_id)
        if not set_clause:
            print("警告: 没有有效的列需要更新")
            return False

        sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"

        # 5. 执行更新
        cursor.execute(sql, params)
        conn.commit()

        return cursor.rowcount == 1

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def is_valid_sql_identifier(identifier: str) -> bool:
    """检查SQL标识符是否合法，防止SQL注入"""
    # SQL标识符通常只允许字母、数字和下划线，且不能以数字开头
    return identifier.replace('_', '').isalnum() and not identifier[0].isdigit()


def record_exists(cursor: sqlite3.Cursor, table_name: str, record_id: int) -> bool:
    """检查记录是否存在"""
    record_id = record_id
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE id = ?", (record_id,))
    return cursor.fetchone() is not None


def get_table_columns(cursor: sqlite3.Cursor, table_name: str) -> List[str]:
    """获取表的列信息"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [column[1] for column in cursor.fetchall()]


def infer_sql_type(value: Any) -> str:
    """根据值推断SQL类型"""
    if value is None:
        # 无法确定类型时默认使用TEXT
        return "TEXT"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    else:
        return "TEXT"


def add_column_to_table(cursor: sqlite3.Cursor, table_name: str, column: str, col_type: str) -> bool:
    """向表中添加新列"""
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {col_type}")
        print(f"已添加新列: {column} ({col_type})")
        return True
    except sqlite3.Error as e:
        print(f"添加列 {column} 失败: {e}")
        return False


def prepare_update_statement(data_dict: Dict[str, Any], record_id: int) -> tuple:
    """准备更新语句和参数"""
    # 过滤掉id字段并确保至少有一个字段需要更新
    update_fields = {k: v for k, v in data_dict.items() if k != "id"}
    if not update_fields:
        return None, None

    set_clause = ", ".join([f"{key} = ?" for key in update_fields.keys()])
    params = list(update_fields.values()) + [record_id]
    return set_clause, params


# # 示例使用
# if __name__ == "__main__":
#     db_path = "doctor_info.db"
#     table_name = "doctor_info"
#
#     # 更新数据示例
#     update_data = {
#         "section": '优质服务中心',  # 存在的列 - 更新数据
#         "new_field": '新添加的值',  # 不存在的列 - 自动添加
#         "another_field": 12345,  # 不存在的列 - 自动添加
#         "state": None  # 存在的列 - 更新为NULL
#     }
#
#     success = smart_update_record_by_id(db_path, table_name, 1, update_data)
#     if success:
#         print("记录更新成功")
#     else:
#         print("记录更新失败")
