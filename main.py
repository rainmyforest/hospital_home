from PIL import Image
from datetime import datetime
import streamlit as st
from my_page.main import login, enroll, find, change


def main():
    st.title("🏥 华北医疗邢台总医院")

    # 设置页面配置
    st.set_page_config(
        page_title="医疗科室信息中心",
        page_icon="🏥",
        # layout="wide",
        initial_sidebar_state="expanded"
    )

    # 获取当前日期和时间
    now = datetime.now()
    # 格式化日期为"年-月-日"的形式，这里使用中文表示
    formatted_date = now.strftime("%Y年%m月%d日")
    # 定义包含样式的HTML内容
    content = f"""
    版本号：2.0.0   
    设计人：闫方涛     
    开展科室：优质服务中心     
    华北医疗邢台总医院       
    联系电话：13313093062    
    {formatted_date}    
    """

    st.sidebar.info(content)

    tab1, tab2, tab3, tab4 = st.tabs(['用户登录', '用户注册', '号码查询', '修改信息'])
    with tab1:
        st.subheader('用户登录')
        login()
        st.image(Image.open('my_data/images/home1.jpg'))
    with tab2:
        st.subheader('欢迎注册')
        enroll()
    with tab3:
        st.subheader('号码查询')
        find()
    with tab4:
        st.subheader('修改信息')
        change()


if __name__ == "__main__":
    main()
