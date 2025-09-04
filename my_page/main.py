import time
import streamlit as st
from my_model.db_sqlite import data_get, data_insert, data_check, data_update
from my_model.by_text import advance_transform
from my_data.user_data import hospital_basic


def login():
    # 未登录时显示登录表单
    doctor_info = data_get.get_data("doctor_info.db", "doctor_info")
    # 如果已登录，显示退出按钮和用户信息
    if "my_info" in st.session_state:
        my_info = st.session_state["my_info"]
        st.success(f"您已登录为: {my_info['name']}，科室: {my_info['section']}")

        if st.button("退出登录"):
            st.session_state.clear()
            st.rerun()

    with st.form("login_form"):
        username = st.text_input("员工号", placeholder="请输入您的5位员工号")
        password = st.text_input("密码", type="password", placeholder="请输入您的密码，初始密码1")
        submitted = st.form_submit_button("登录")

        if submitted:
            # 验证输入是否为空
            if not username or not password:
                st.error("请输入用户名和密码")
                return False

            # 验证用户名和密码是否为数字
            if not username.isdigit() or not password.isdigit():
                st.error("用户名和密码必须为数字")
                return False

            # 验证用户名长度是否为5位
            if len(username) != 5:
                st.error("员工号必须是5位数字")
                return False

            # 检查用户名是否存在
            username = int(username)
            if username not in doctor_info["number"].values:
                st.error("员工号不存在")
                return False

            # 获取密码并验证
            my_info = doctor_info[doctor_info["number"] == username].iloc[0]
            stored_password = str(my_info["password"])
            if stored_password == password:
                st.success(f"欢迎，{my_info["name"]}！员工号{username} - 登录成功。")
                my_info["state"] = advance_transform.base_converter(str(my_info["state"]), 10, 2)
                st.session_state["my_info"] = my_info
                return True

            else:
                st.error("密码错误")
                return False


def enroll():

    with st.form("doctor_registration_form"):
        # 表单输入字段
        name = st.text_input("姓名", key="name")
        section = st.selectbox(
            "科室", hospital_basic.section,
            key="section"
        )
        number = st.number_input("员工号", min_value=1, step=1, format="%d", key="number")

        # 添加密码字段
        password = st.text_input("密码", type="password", key="password")
        confirm_password = st.text_input("确认密码", type="password", key="confirm_password")

        submitted = st.form_submit_button("注册")

        if submitted:
            # 检查所有必填字段和密码匹配
            if not name or not number or not password or not confirm_password:
                st.error("请填写完整信息！")
            elif len(str(number)) != 5:  # 新增：验证员工号必须为5位数
                st.error("员工号必须是5位数！")
            elif password != confirm_password:
                st.error("两次输入的密码不一致！")
            else:
                # 准备用户数据（使用实际密码）
                user_data = {
                    "name": name,
                    "number": number,
                    "section": section,
                    "password": password,  # 使用实际输入的密码
                    "state": -1
                }
                conditions = {"name": name, "number": number}
                exists = data_check.check_existence('doctor_info.db', 'doctor_info', conditions, match_all=False)
                if exists.empty:
                    # 插入数据（表不存在时会自动创建）
                    row_id = data_insert.insert_into_table('doctor_info.db', 'doctor_info', user_data)
                    st.success(f'注册成功，您是我院第{row_id}员工，请登录')
                else:
                    st.warning("此账号已注册，若有疑问联系管理员")


def find():
    doctor_info = data_get.get_data("doctor_info.db", "doctor_info")
    name = st.text_input("请输入您的姓名：")
    if name:
        df = doctor_info[doctor_info["name"] == name]
        if df.empty:
            st.warning('这里没有您的信息，请联系人事部门要到员工号和所在部门，再在系统上注册')
        else:
            if len(df) > 1:
                number = st.selectbox('请选择您的员工号：', df['number'].values)
                df = df[df["number"] == number]
            info = df.iloc[0]
            st.info(f"员工{info['name']}，所属科室{info['section']}，员工号{info['number']}")


def change():
    if "my_info" not in st.session_state:
        st.warning('用户请先登录')
    else:
        my_info = st.session_state["my_info"]
        with st.form("doctor_change_form"):
            st.subheader("修改个人信息")

            # 姓名输入框
            name = st.text_input("姓名", value=my_info["name"], key="name1")

            # 科室选择框
            # 确保my_info["section"]存在于hospital_section.section中
            section_index = 0
            if my_info["section"] in hospital_basic.section:
                section_index = hospital_basic.section.index(my_info["section"])

            section = st.selectbox(
                "科室",
                hospital_basic.section,
                index=section_index,
                key="section1"
            )

            number = st.number_input("员工号", value=my_info['number'], min_value=1, step=1, format="%d", key="number1")

            # 密码修改部分
            st.info("密码（留空表示不修改密码）")
            password = st.text_input("新密码", type="password", key="password1", placeholder="输入新密码")
            confirm_password = st.text_input("确认新密码", type="password", key="confirm_password1",
                                             placeholder="再次输入新密码")

            submitted = st.form_submit_button("确认修改")

            if submitted:
                # 检查必填字段
                if not name:
                    st.error("姓名不能为空！")
                # 检查密码是否一致（如果填写了密码）
                elif password and password != confirm_password:
                    st.error("两次输入的密码不一致！")
                else:
                    # 准备用户数据
                    user_data = {
                        "name": name,
                        "section": section,
                        "number": number,
                    }

                    # 只有在输入了新密码时才更新密码字段
                    if password:
                        user_data["password"] = password

                    # 更新数据库
                    success = data_update.smart_update_record_by_id(
                        "doctor_info.db", "doctor_info", int(my_info['id']), user_data
                    )

                    if success:
                        # 更新session_state中的用户信息
                        st.success('信息修改成功！')
                        st.session_state.clear()
                        time.sleep(3)
                        st.rerun()  # 刷新页面以显示更新后的信息
                    else:
                        st.error("信息修改失败，请重试或联系管理员")