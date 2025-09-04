# 用python写一个delete函数，控制sqlite数据库删除一行数据，参数为数据库名database_path, 表名table_name，id
import sqlite3


def delete_data(database_path, table_name, id):
    """
    从SQLite数据库中删除指定表的一行数据

    参数:
        database_path (str): 数据库文件路径
        table_name (str): 目标表名称
        id (int): 要删除的数据行的ID

    返回:
        bool: 成功删除返回True，失败返回False
    """
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # 使用参数化查询防止SQL注入
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, (id,))

        # 检查是否成功删除
        if cursor.rowcount > 0:
            # 提交事务
            conn.commit()
            return True
        else:
            # 未找到记录，回滚事务
            conn.rollback()
            return False

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        # 关闭连接
        if conn:
            conn.close()


# # 使用示例
# if __name__ == "__main__":
#     result = delete_data("example.db", "users", 1)
#     if result:
#         print("删除成功")
#     else:
#         print("删除失败")