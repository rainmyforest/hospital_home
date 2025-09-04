import time

import streamlit as st
from my_model.db_sqlite import data_check, data_update
from my_model.by_text import advance_transform
from my_data.user_data import pages_json


def update_state(doctor_id, doctor_state):
    function = [page['name'] for page in pages_json.DEFAULT_PAGES]
    str_state1 = advance_transform.base_converter(str(doctor_state), 10, 2)
    box = {'普通用户': '0', '管理员': '1'}

    with st.form(key='update_state'):
        # 创建一个列表来存储新的状态值
        new_states = ''

        for i in range(len(str_state1)):
            # 为每个选择框创建唯一键
            key = f"state_{i}"  # 添加索引确保唯一性
            # 获取当前选择框的值
            selected = st.selectbox(
                f"{function[i]}",
                box,
                index=list(box.values()).index(str_state1[i]),
                key=key
            )
            new_states = new_states + box[selected]  # 取消注释这行来收集选择的值

        # 表单提交按钮
        if st.form_submit_button('点击更新状态数据'):
            str_state2 = advance_transform.base_converter(new_states, 2, 10)
            condition = {'state': int(str_state2)}
            success = data_update.smart_update_record_by_id('doctor_info.db', 'doctor_info', int(doctor_id), condition)
            if success:
                st.success('更新数据成功')
            else:
                st.warning('更新数据失败')
            time.sleep(2)
            st.rerun()


def get_data():
    # 获取用户输入的字符串
    number_str = st.text_input('请输入5位员工号：')

    if number_str:  # 检查是否有输入
        try:
            # 尝试转换为整数
            number = int(number_str)

            # 验证是否为5位数字
            if len(number_str) == 5:
                conditions = {"number": number}
                doctor_info = data_check.check_existence('doctor_info.db', 'doctor_info', conditions).iloc[0]
                doctor_state = doctor_info['state']
                doctor_id = doctor_info['id']

                update_state(doctor_id, doctor_state)

            else:
                st.error("请输入5位数字的员工号")

        except ValueError:
            st.error("请输入有效的数字")


def main():
    get_data()


if __name__ == '__main__':
    main()
