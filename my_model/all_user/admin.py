import streamlit as st


def administrator(ordinal, types=0):
    # ordinal 为第几个项目
    if types == 0:
        # 未登录也可以看
        return True
    elif types > 0:
        if 'user_info' in st.session_state:
            # 获取当前用户信息
            user_info = st.session_state['user_info']
            bin_str = user_info['state']

            # 检查索引是否有效
            if ordinal - 1 < len(bin_str):
                admin = bin_str[ordinal - 1] == '1'
            else:
                admin = False  # 索引超出范围，默认无权限

            if types == 1:
                # 有用户登录信息的可以看
                return True
            elif types == 2 and admin:
                # 用户为本项目管理员的可以看
                return True
            else:
                return False
        else:
            return False
