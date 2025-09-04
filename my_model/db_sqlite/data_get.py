import sqlite3
import pandas as pd


def get_data(database_path, table_name):
    """
    直接从 SQLite 数据库读取表到 DataFrame

    参数:
        database_path (str): SQLite 数据库文件路径
        table_name (str): 要读取的表名

    返回:
        pd.DataFrame: 包含表数据的 DataFrame，异常时返回 None
    """
    try:
        # 创建数据库连接
        conn = sqlite3.connect(database_path)

        # 使用参数化查询避免 SQL 注入
        query = f"SELECT * FROM `{table_name}`"  # 使用反引号处理特殊表名

        # 直接读取表数据到 DataFrame
        df = pd.read_sql_query(query, conn)
        return df

    except sqlite3.Error as e:
        # 捕获 SQLite 错误
        print(f"SQLite 错误: {str(e)}")
        return None
    except pd.errors.DatabaseError as e:
        # 捕获 pandas 数据库错误
        print(f"数据库读取错误: {str(e)}")
        return None
    except Exception as e:
        # 捕获其他所有异常
        print(f"意外错误: {str(e)}")
        return None
    finally:
        # 确保连接关闭
        if 'conn' in locals():
            conn.close()


# # 使用示例
# if __name__ == "__main__":
#     # 测试用例
#     db_path = "example.db"
#     table = "users"
#
#     # 获取表数据
#     df = get_table_from_sqlite(db_path, table)
#
#     if df is not None:
#         print(f"成功读取表 '{table}' ({len(df)} 行)")
#         print(df.head())
#     else:
#         print(f"无法读取表 '{table}'")

def get_last_row(database_path, table_name):
    try:
        # 连接到数据库
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # 获取 doctor_forms 表的最后一行数据
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY ROWID DESC LIMIT 1")
        last_row = cursor.fetchone()

        if last_row:
            # 在关闭连接前获取列名（修正表名为doctor_forms）
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            # 将最后一行数据转换为 DataFrame
            df = pd.DataFrame([last_row], columns=columns)

            # 关闭连接
            conn.close()
            return df

        # 如果没有数据也关闭连接
        conn.close()
        return None

    except sqlite3.Error as e:
        print(f"SQLite 错误: {e}")
        return None
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None


# def index_main():
#
#     df1 = db_sqlite.get_last_row("complaints.db", "complaints")
#     date = datetime.date.today()
#     date_str = date.strftime("%Y%m%d")
#
#     if df1 is not None:
#         old_str = df1["index_id"][0]
#         if date_str == old_str[0:8]:
#             index_id = str(int(df1["index_id"].iloc[0]) + 1)
#             st.write(index_id)
#         else:
#             index_id = date_str + '001'
#
#     else:
#         # 将日期对象转换为不带'-'的字符串
#         index_id = date_str + '001'
#     return index_id
