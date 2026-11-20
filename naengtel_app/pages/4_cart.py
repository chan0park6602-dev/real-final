"""장보기 목록 화면: 선택한 메뉴들의 부족 재료를 중복 없이 모으고 비용 합산 (명세서 14~17번).
데스크톱 구성: 왼쪽 장보기 표, 오른쪽 예상 비용 요약."""
import streamlit as st

import common
import core

common.setup("장보기 목록")
_, recipes, _, _, category_map = common.get_data()
ss = st.session_state
by_id = recipes.set_index("recipe_id")


def uncart(rid):
    if rid in ss.cart:
        ss.cart.remove(rid)


def set_checked(name):
    on = ss[f"chk-{name}"]
    if on and name not in ss.checked:
        ss.checked.append(name)
    elif not on and name in ss.checked:
        ss.checked.remove(name)


def reset():
    ss.cart = []
    ss.checked = []


def put_in_fridge():
    """체크한(산) 재료를 냉장고에 넣고, 이제 재료가 다 갖춰진 메뉴는 목록에서 뺀다."""
    bought = [x["name"] for x in common.shopping_list() if x["name"] in ss.checked]
    for name in bought:
        if name not in ss.inventory:
            ss.inventory.append(name)
    ss.checked = []
    own = common.owned()
    ss.cart = [rid for rid in ss.cart if core.find_missing_ingredients(by_id.loc[rid, "ingredients"], own)]
    st.toast(f"{len(bought)}개 재료를 냉장고에 넣었어요")


items = common.shopping_list()
total = sum(x["price"] for x in items)
common.page_head("부족한 재료만 모았어요", "장보기 목록",
                 "여러 메뉴에 같은 재료가 필요해도 한 번만 담아요.",
                 kpis=[("선택한 메뉴", f"{len(ss.cart)}개", ""), ("살 재료", f"{len(items)}개", "o")])

if not ss.cart:
    with st.container(border=True):
        common.empty("🛒", "아직 고른 메뉴가 없어요.<br>추천 화면이나 메뉴 검색에서 '장보기'를 눌러 담아 주세요.")
        st.page_link("pages/2_recommend.py", label="추천 메뉴 보러 가기", icon="👨‍🍳")
    st.stop()

left, right = st.columns([2.4, 1], gap="large")

with left:
    with st.container(border=True):
        common.panel_title("선택한 메뉴", f"{len(ss.cart)}개 · 누르면 목록에서 빠져요")
        cols = st.columns(4)
        for i, rid in enumerate(ss.cart):
            row = by_id.loc[rid]
            cols[i % 4].button(f"{row['emoji']} {row['name']}  ✕", key=f"un-{rid}", on_click=uncart, args=(rid,),
                               use_container_width=True)

    with st.container(border=True):
        common.panel_title("살 것", f"{len(items)}개")
        if not items:
            common.empty("🎉", "고른 메뉴의 재료가 이미 다 있어요!")
        else:
            widths = [0.5, 2, 1.3, 3.4, 1.2]
            for col, h in zip(st.columns(widths), ["", "재료", "분류", "필요한 메뉴", "예상 가격"]):
                col.markdown(f'<div class="nt-th">{h}</div>', unsafe_allow_html=True)
            for x in items:
                c0, c1, c2, c3, c4 = st.columns(widths, vertical_alignment="center")
                done = x["name"] in ss.checked
                c0.checkbox("샀음", value=done, key=f"chk-{x['name']}", on_change=set_checked, args=(x["name"],),
                            label_visibility="collapsed")
                c1.markdown(f"~~{x['name']}~~" if done else f"**{x['name']}**")
                cat = category_map.get(x["name"], "")
                c2.markdown(f"{common.CATEGORY_EMOJI.get(cat, '')} {cat}")
                c3.markdown(f":gray[{' · '.join(x['for'])}]")
                c4.markdown(f"<div style='text-align:right'>약 {core.won(x['price'])}</div>", unsafe_allow_html=True)

with right:
    with st.container(border=True):
        st.markdown('<div class="nt-label">예상 총 비용</div>'
                    f'<div class="nt-total">약 {core.won(total)}</div>', unsafe_allow_html=True)
        left_to_buy = sum(x["price"] for x in items if x["name"] not in ss.checked)
        if items and left_to_buy != total:
            st.caption(f"체크 안 한 재료만 약 {core.won(left_to_buy)}")
        for x in items:
            st.markdown(f'<div class="nt-side-stat"><span>{x["name"]}</span><span>{core.won(x["price"])}</span></div>',
                        unsafe_allow_html=True)
        st.write("")
        if any(x["name"] in ss.checked for x in items):
            st.button("체크한 재료 냉장고에 넣기", type="primary", use_container_width=True, on_click=put_in_fridge)
        st.button("목록 초기화", use_container_width=True, on_click=reset)
        st.markdown('<p class="nt-fine">실시간 판매가격이 아닌 자체 기준가격을 활용한 예상값입니다.</p>',
                    unsafe_allow_html=True)
