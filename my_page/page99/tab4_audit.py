import time

import streamlit as st
from my_model.db_sqlite import data_get, data_update, data_delete


def get_data(num):
    data = data_get.get_data('doctor_info.db', 'doctor_info')
    my_data = data[data['state'] <= num]
    return my_data


def update_data(my_data):
    my_dict = {}
    for row in my_data.itertuples(index=True, name='RowData'):
        # st.write(row)
        my_dict[f"姓名-{row.name}，科室-{row.section}，id-{row.number}"] = row.id
    my_list = st.multiselect('请选择通过审核的人员：', my_dict)
    col1, col2 = st.columns(2)
    with col1:
        if st.button('点击激活新注册人员'):
            for i in my_list:
                # 更新数据示例
                data = {
                    "state": 0,  # 存在的列 - 更新数据
                }

                success = data_update.smart_update_record_by_id('doctor_info.db', 'doctor_info', my_dict[i], data)
                if success:
                    st.success(f'已激活新注册人员：{i}')
                else:
                    st.error("记录更新失败")
            time.sleep(2)
            st.rerun()
    with col2:
        if st.button('点击删除待审核人员'):
            for i in my_list:

                success = data_delete.delete_data('doctor_info.db', 'doctor_info', my_dict[i])
                if success:
                    st.success(f'已删除待审核人员：{i}')
                else:
                    st.error("记录删除失败")
            time.sleep(2)
            st.rerun()


def main():
    my_data = get_data(-1)
    update_data(my_data)


if __name__ == '__main__':
    main()
