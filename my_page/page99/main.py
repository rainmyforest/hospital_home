import streamlit as st
from my_page.page99 import tab1_see, tab2_open, tab3_state, tab4_audit


def main():
    if 'my_info' in st.session_state:
        my_info = st.session_state.my_info
        if my_info['name'] == '闫方涛':
            tab1, tab2, tab3, tab4 = st.tabs(['管理看板', '页面控制', '状态修改', '准入审核'])
            with tab1:
                st.title("📄 管理看板")
                tab1_see.main()
            with tab2:
                st.title("📄 页面控制")
                tab2_open.main()
            with tab3:
                st.title("📄 状态修改")
                tab3_state.main()
            with tab4:
                st.title("📄 准入审核")
                tab4_audit.main()
        else:
            st.warning('您不是系统管理员')
    else:
        st.warning('请您先登录')


if __name__ == '__main__':
    main()
