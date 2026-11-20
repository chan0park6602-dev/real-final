"""메뉴 검색 화면: 먹고 싶은 메뉴를 찾아 재료 비교·대체 재료 확인 (명세서 12·13번).
데스크톱 구성: 왼쪽 검색 결과 목록, 오른쪽 넓은 상세 화면."""
import streamlit as st

import common
import core

common.setup("메뉴 검색")
_, recipes, _, _, _ = common.get_data()
ss = st.session_state
MAX_RESULTS = 60


def select(rid):
    ss.search_sel = rid


common.page_head("먹고 싶은 게 따로 있다면", "메뉴 검색",
                 "메뉴를 고르면 필요한 재료, 내가 가진 재료, 부족한 재료와 대체 재료를 한 번에 보여 드려요.")

left, right = st.columns([1, 2.6], gap="large")

with left:
    with st.container(border=True):
        query = st.text_input("메뉴 검색", placeholder="🔍  먹고 싶은 메뉴를 검색해보세요", label_visibility="collapsed")
        results = core.search_recipe(recipes, query)
        st.caption(f"{len(results)}개 메뉴" + (f" · 위에서 {MAX_RESULTS}개만 표시" if len(results) > MAX_RESULTS else ""))
        if results.empty:
            common.empty("🤔", "찾는 메뉴가 없어요.<br>재료 이름으로도 검색할 수 있어요.")
        else:
            ids = results["recipe_id"].tolist()
            if ss.get("search_sel") not in ids:
                ss.search_sel = ids[0]
            own = common.owned()
            with st.container(height=560, border=False):
                for _, row in results.head(MAX_RESULTS).iterrows():
                    n_miss = len(core.find_missing_ingredients(row["ingredients"], own))
                    status = "✓ 100%" if n_miss == 0 else f"+{n_miss}개"
                    st.button(f"{row['emoji']}  {row['name']}   ·   {status}", key=f"res-{row['recipe_id']}",
                              type="primary" if row["recipe_id"] == ss.search_sel else "secondary",
                              use_container_width=True, on_click=select, args=(row["recipe_id"],))

with right:
    with st.container(border=True):
        if results.empty:
            common.empty("🔍", "왼쪽에서 메뉴를 검색해 주세요.")
        else:
            common.render_compare(ss.search_sel, key="search")
