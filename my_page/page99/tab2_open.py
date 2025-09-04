import streamlit as st
import json
import os
from pathlib import Path
from my_data.user_data import pages_json

DEFAULT_PAGES = pages_json.DEFAULT_PAGES


def load_page_data():
    """从JSON文件加载页面数据，如果文件不存在则创建默认数据"""
    json_file = "pages_config.json"

    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PAGES, f, ensure_ascii=False, indent=4)
        return DEFAULT_PAGES

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            pages = json.load(f)
            # 确保所有页面都有template字段（向后兼容）
            for page in pages:
                if "template" not in page:
                    page["template"] = f"templates/{page['file'].replace('.py', '_template.py')}"
            return pages
    except:
        return DEFAULT_PAGES


def save_page_data(pages):
    """保存页面数据到JSON文件"""
    with open("pages_config.json", 'w', encoding='utf-8') as f:
        json.dump(pages, f, ensure_ascii=False, indent=4)


def get_template_content(template_path):
    """从模板文件读取内容，如果模板不存在则返回默认内容"""
    if os.path.exists(template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            st.error(f"读取模板文件失败: {template_path}")
            # 返回更简单的默认内容
            return f"import streamlit as st\n\nst.title('页面标题')\nst.write('这是默认页面内容。')"

    # 如果模板文件不存在，尝试创建默认模板
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    default_content = f"import streamlit as st\n\nst.title('{Path(template_path).stem.replace('_template', '')}')\nst.write('这是{Path(template_path).stem.replace('_template', '')}页面。')"

    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
        return default_content
    except:
        st.error(f"创建模板文件失败: {template_path}")
        return f"import streamlit as st\n\nst.title('页面标题')\nst.write('这是默认页面内容。')"


def update_pages_directory(pages, force_update=False):
    """根据配置更新pages目录中的文件，使用模板文件生成内容

    Args:
        pages: 页面配置列表
        force_update: 是否强制更新所有页面文件，即使已存在
    """
    pages_dir = Path("pages")
    templates_dir = Path("templates")

    # 确保pages和templates目录存在
    if not pages_dir.exists():
        pages_dir.mkdir()
    if not templates_dir.exists():
        templates_dir.mkdir()
        st.warning("模板目录不存在，已创建空目录。")

    # 获取配置中所有有效的页面文件名
    configured_files = {page["file"] for page in pages}

    # 获取pages目录中现有的所有.py文件
    existing_files = {f.name for f in pages_dir.glob("*.py") if f.is_file()}

    # 删除不在配置中的页面文件
    for file_to_remove in existing_files - configured_files:
        (pages_dir / file_to_remove).unlink()
        st.info(f"已删除不在配置中的页面: {file_to_remove}")

    # 只处理配置中提到的文件
    for page in pages:
        page_file = pages_dir / page["file"]
        template_file = Path(page.get("template", f"templates/{page['file'].replace('.py', '_template.py')}"))

        if page["enabled"]:
            # 如果文件不存在或强制更新，从模板创建/更新文件
            if not page_file.exists() or force_update:
                template_content = get_template_content(template_file)
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(template_content)
                st.info(f"已生成页面: {page_file}")
        else:
            # 如果文件存在且被禁用，删除它
            if page_file.exists():
                page_file.unlink()
                st.info(f"已删除页面: {page_file}")


def apply_template_to_selected_pages(pages, template_path):
    """应用指定模板到使用此模板的所有页面

    Args:
        pages: 页面配置列表
        template_path: 要应用的模板路径
    """
    # 找到所有使用此模板的页面
    pages_to_update = [page for page in pages if page.get("template") == template_path]

    if not pages_to_update:
        st.warning("没有页面使用此模板!")
        return pages

    # 强制更新这些页面
    update_pages_directory(pages_to_update, force_update=True)

    st.success(f"已应用模板到 {len(pages_to_update)} 个页面!")
    return pages


def main():
    st.markdown("使用此界面管理应用程序中的页面可见性和编辑模板。")

    # 加载页面数据
    pages = load_page_data()

    # 创建选项卡布局
    tab1, tab2 = st.tabs(["页面管理", "模板编辑器"])

    with tab1:
        # 创建两列布局
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("页面列表")
            st.markdown("启用或禁用应用程序中的页面。")

            # 显示页面列表和切换开关
            for i, page in enumerate(pages):
                enabled = st.checkbox(
                    f"{page['name']} (`{page['file']}`)",
                    value=page["enabled"],
                    key=f"page_{i}"
                )
                pages[i]["enabled"] = enabled

        with col2:
            st.subheader("操作")

            # 保存按钮
            if st.button("💾 保存配置", use_container_width=True):
                save_page_data(pages)
                update_pages_directory(pages)
                st.success("配置已保存并应用！")
                st.rerun()

            # 重置按钮
            if st.button("🔄 重置为默认", use_container_width=True):
                save_page_data(DEFAULT_PAGES)
                # 强制更新所有页面文件
                update_pages_directory(DEFAULT_PAGES, force_update=True)
                st.success("已重置为默认配置！")
                st.rerun()

            # 重新生成所有页面按钮
            if st.button("🔄 重新生成所有页面", use_container_width=True):
                update_pages_directory(pages, force_update=True)
                st.success("已重新生成所有页面！")
                st.rerun()

            st.divider()

            # 显示当前状态
            st.subheader("当前状态")
            enabled_count = sum(1 for p in pages if p["enabled"])
            disabled_count = len(pages) - enabled_count

            st.metric("已启用页面", enabled_count)
            st.metric("已禁用页面", disabled_count)

        # 显示JSON数据（可选）
        with st.expander("查看JSON数据"):
            st.json(pages)

    with tab2:
        st.subheader("模板编辑器")

        # 选择要编辑的模板
        template_options = {page["template"]: f"{page['name']} ({page['template']})" for page in pages}
        selected_template = st.selectbox(
            "选择要编辑的模板",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            key="template_selector"
        )

        if selected_template:
            template_path = selected_template

            # 确保模板文件存在
            if not os.path.exists(template_path):
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(
                        f"# {Path(template_path).stem.replace('_template', '')}页面模板\nimport streamlit as st\n\nst.title('{Path(template_path).stem.replace('_template', '')}')\nst.write('这是{Path(template_path).stem.replace('_template', '')}页面。')")

            # 读取模板内容
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except Exception as e:
                st.error(f"读取模板文件失败: {e}")
                template_content = f"# 错误: 无法读取文件 {template_path}"

            # 编辑器
            new_content = st.text_area(
                "模板内容",
                template_content,
                height=400,
                key="template_editor"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 保存模板", use_container_width=True):
                    try:
                        with open(template_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        st.success("模板已保存!")
                    except Exception as e:
                        st.error(f"保存模板失败: {e}")

            with col2:

                if st.button("📄 重新生成并使用模板", use_container_width=True):
                    # 应用当前模板到所有使用此模板的页面
                    update_pages_directory(pages, force_update=True)
                    st.success("已重新生成所有页面！")
                    st.rerun()

            # 显示模板文件信息
            st.divider()
            st.subheader("模板信息")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**文件路径:** {template_path}")
                if os.path.exists(template_path):
                    file_size = os.path.getsize(template_path)
                    st.write(f"**文件大小:** {file_size} 字节")
                    st.write(f"**最后修改:** {os.path.getmtime(template_path):.0f}")
                else:
                    st.write("**文件状态:** 不存在")

            with col2:
                # 显示使用此模板的页面
                using_pages = [page["name"] for page in pages if page.get("template") == template_path]
                st.write(f"**使用此模板的页面:** {', '.join(using_pages) if using_pages else '无'}")


if __name__ == "__main__":
    main()