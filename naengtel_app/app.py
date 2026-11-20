"""냉털메이트 실행 파일.

실행:  streamlit run app.py
네 화면을 st.navigation으로 등록하고, 왼쪽 기본 메뉴는 숨긴 채 직접 만든 메뉴(common.py)를 쓴다.
첫 화면은 랜딩페이지 없이 바로 '재고 관리(내 냉장고)'로 들어간다 (명세서 27번).
"""
import streamlit as st

st.set_page_config(page_title="냉털메이트", page_icon="🧊", layout="wide", initial_sidebar_state="auto")

pages = [
    st.Page("pages/1_fridge.py", title="재고 관리", icon="🧊", url_path="fridge", default=True),
    st.Page("pages/2_recommend.py", title="레시피 추천", icon="👨‍🍳", url_path="recommend"),
    st.Page("pages/3_search.py", title="메뉴 검색", icon="🔍", url_path="search"),
    st.Page("pages/4_cart.py", title="장보기 목록", icon="🛒", url_path="cart"),
]
st.navigation(pages, position="hidden").run()
