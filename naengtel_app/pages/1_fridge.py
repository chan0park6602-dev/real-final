"""재고 관리 화면: 보유 식재료 추가·삭제, 기본 재료 설정 (명세서 5·6번).

데스크톱 구성: 왼쪽 넓은 영역에서 분류별로 재료를 클릭해 담고,
오른쪽 패널에서 '내 냉장고'와 기본 재료를 확인한다.
"""
import streamlit as st

import common
import core

common.setup("재고 관리")
ingredients, recipes, _, price_map, category_map = common.get_data()
ss = st.session_state
PER_ROW = 6


# ── 동작 ──
def add_from_search():
    name = ss.get("add_select")
    if name and name not in ss.inventory:
        ss.inventory.append(name)
        st.toast(f"{name} 담았어요")
    ss.add_select = None   # 검색창 비우기


def clear_all():
    ss.inventory = []


def set_basic(name):
    on = ss[f"basic-{name}"]
    if on and name not in ss.basics:
        ss.basics.append(name)
    elif not on and name in ss.basics:
        ss.basics.remove(name)


# ── 화면 ──
ranked = core.recommend_recipes(recipes, common.owned(), price_map)
has_inv = bool(ss.inventory)
common.page_head(
    "냉동실 속 간편식도, 그럴듯한 한 끼로!", "내 냉장고",
    "컵라면·3분카레·냉동만두처럼 쟁여 둔 간편식에 남은 재료만 더해도 근사한 요리가 돼요.<br>가지고 있는 재료를 눌러 담아 주세요.",
    kpis=[("담은 재료", f"{len(ss.inventory)}개", ""),
          ("바로 만들 수 있는 메뉴", f"{int((ranked['missing_count'] == 0).sum()) if has_inv else 0}개", "g"),
          ("1개만 더 사면", f"{int((ranked['missing_count'] == 1).sum()) if has_inv else 0}개", "o")],
)

left, right = st.columns([2.4, 1], gap="large")

with left:
    with st.container(border=True):
        common.panel_title("재료 고르기", "검색하거나 아래에서 눌러 담으세요. 다시 누르면 빠져요.")
        choices = ingredients.loc[~ingredients["basic"] & ~ingredients["name"].isin(ss.inventory), "name"].tolist()
        st.selectbox("식재료 검색", choices, index=None, key="add_select", on_change=add_from_search,
                     placeholder="🔍  보유한 식재료를 검색해보세요", label_visibility="collapsed")

        tabs = st.tabs([label for label, _ in common.PICKER_TABS])
        for tab, (_, cats) in zip(tabs, common.PICKER_TABS):
            with tab:
                for cat in cats:
                    names = ingredients.loc[(ingredients["category"] == cat) & ~ingredients["basic"], "name"].tolist()
                    if not names:
                        continue
                    st.markdown(f'<div class="nt-label">{common.CATEGORY_EMOJI.get(cat, "")} {cat}</div>',
                                unsafe_allow_html=True)
                    for i in range(0, len(names), PER_ROW):
                        cols = st.columns(PER_ROW)
                        for col, name in zip(cols, names[i:i + PER_ROW]):
                            mine = name in ss.inventory
                            col.button(f"✓ {name}" if mine else name, key=f"pick-{name}",
                                       type="primary" if mine else "secondary", use_container_width=True,
                                       on_click=common.toggle_inventory, args=(name,))

with right:
    with st.container(border=True):
        common.panel_title("🧊 내 냉장고", f"{len(ss.inventory)}개")
        if not has_inv:
            common.empty("🫙", "아직 비어 있어요.<br>왼쪽에서 재료를 눌러 담아 주세요.")
        else:
            groups = {}
            for name in ss.inventory:
                groups.setdefault(category_map.get(name, "기타"), []).append(name)
            order = list(common.CATEGORY_EMOJI)
            with st.container(height=330, border=False):
                for cat in sorted(groups, key=lambda c: order.index(c) if c in order else 99):
                    st.markdown(f'<div class="nt-label">{common.CATEGORY_EMOJI.get(cat, "")} {cat}</div>',
                                unsafe_allow_html=True)
                    cols = st.columns(3)
                    for i, name in enumerate(groups[cat]):
                        cols[i % 3].button(f"{name} ✕", key=f"del-{name}", help=f"{name} 빼기",
                                           use_container_width=True, on_click=common.toggle_inventory, args=(name,))
            st.button("모두 비우기", on_click=clear_all, use_container_width=True)

    with st.container(border=True):
        common.panel_title("🧂 기본 재료", "늘 있다고 보고 계산")
        cols = st.columns(2)
        for i, name in enumerate(ingredients.loc[ingredients["basic"], "name"]):
            cols[i % 2].checkbox(name, value=name in ss.basics, key=f"basic-{name}", on_change=set_basic, args=(name,))

    if st.button("이 재료로 메뉴 추천받기  →", type="primary", use_container_width=True, disabled=not has_inv):
        st.switch_page("pages/2_recommend.py")
    if not has_inv:
        st.caption("재료를 하나 이상 담으면 추천을 받을 수 있어요.")
