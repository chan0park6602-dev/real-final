"""레시피 추천 화면: 부족 재료 수 → 추가 비용 순으로 정렬해 구역별로 보여 준다 (명세서 7~10번).
데스크톱 구성: 한 줄에 카드 5장."""
import streamlit as st

import common
import core

common.setup("레시피 추천")
_, recipes, _, price_map, _ = common.get_data()
ss = st.session_state

GROUPS = [   # (제목, 설명, 처음 보여 줄 카드 수)
    ("✅ 지금 바로 만들 수 있어요", "추가 비용 없이 바로", 10),
    ("🛒 1개만 더 사면 돼요", "장보기 한 번이면 충분해요", 10),
    ("🧺 재료 2개가 더 필요해요", "조금만 더 사면 돼요", 5),
    ("🧺 재료 3개 이상 더 필요해요", "다음 장보기 때 참고하세요", 5),
]
PER_ROW = 5


def show_more(key):
    ss[key] = ss.get(key, 0) + 10


all_ranked = core.recommend_recipes(recipes, common.owned(), price_map)
common.page_head(
    "간편식 하나로 오늘 한 끼 업그레이드", "내 재료로 만들 수 있는 메뉴",
    "부족한 재료가 적은 메뉴부터, 같으면 추가 비용이 싼 메뉴부터 보여 드려요.<br>🍱 표시는 간편식·냉동식품을 활용한 레시피예요.",
    kpis=[("바로 가능", f"{int((all_ranked['missing_count'] == 0).sum())}개", "g"),
          ("1개만 더", f"{int((all_ranked['missing_count'] == 1).sum())}개", "o"),
          ("전체 레시피", f"{len(all_ranked)}개", "")],
)

if not ss.inventory:
    with st.container(border=True):
        common.empty("🧊", "냉장고가 비어 있어서 모든 메뉴에 재료가 부족해요.<br>먼저 가진 재료를 담아 주세요.")
        st.page_link("pages/1_fridge.py", label="재료 담으러 가기", icon="🧊")
    st.stop()

bar_l, bar_r = st.columns([3, 1], vertical_alignment="center")
with bar_l:
    counts = all_ranked["cuisine"].value_counts()
    def _count(c):
        if c == "전체":
            return len(all_ranked)
        if c == core.QUICK_LABEL:
            return int(all_ranked["quick"].sum())
        return int(counts.get(c, 0))
    labels = {c: f"{c} {_count(c)}" for c in common.CUISINES}
    st.radio("음식 분류", common.CUISINES, horizontal=True, key="cuisine",
             format_func=labels.get, label_visibility="collapsed")
with bar_r:
    shown = ", ".join(ss.inventory[:6]) + (f" 외 {len(ss.inventory) - 6}개" if len(ss.inventory) > 6 else "")
    st.caption(f"내 재료: {shown}")

ranked = core.recommend_recipes(recipes, common.owned(), price_map, ss.cuisine)
if ranked.empty:
    common.empty("🍽️", "이 분류에는 레시피가 없어요.")

for k, (title, desc, base_limit) in enumerate(GROUPS):
    group = ranked[ranked["missing_count"] == k] if k < 3 else ranked[ranked["missing_count"] >= 3]
    if group.empty:
        continue
    st.markdown(f'<div class="nt-group nt-g{k}">{title}<em>{desc}</em><span>{len(group)}개</span></div>',
                unsafe_allow_html=True)
    more_key = f"more-{ss.cuisine}-{k}"
    limit = base_limit + ss.get(more_key, 0)
    rows = group.head(limit).to_dict("records")
    for i in range(0, len(rows), PER_ROW):
        cols = st.columns(PER_ROW)
        for col, row in zip(cols, rows[i:i + PER_ROW]):
            with col:
                common.recipe_card(row, key=f"rec{k}")
    if len(group) > limit:
        _, mid, _ = st.columns([2, 1, 2])
        mid.button(f"더 보기 ({len(group) - limit}개 남음)", key=f"btn-{more_key}", on_click=show_more,
                   args=(more_key,), use_container_width=True)
