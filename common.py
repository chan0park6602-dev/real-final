"""모든 화면이 함께 쓰는 부분: 데이터 캐시, 사용자 상태, 디자인(CSS), 왼쪽 메뉴, 레시피 카드·상세.

노트북·데스크톱 화면(가로 1280px 이상)을 기준으로 디자인했다.
왼쪽에 고정 메뉴, 오른쪽에 넓은 작업 영역을 두는 대시보드형 구성.
"""
import streamlit as st

import core
from core import BASE_DIR

LOGO = BASE_DIR / "images" / "logo.png"

PAGES = [
    ("pages/1_fridge.py", "재고 관리", "🧊"),
    ("pages/2_recommend.py", "레시피 추천", "👨‍🍳"),
    ("pages/3_search.py", "메뉴 검색", "🔍"),
    ("pages/4_cart.py", "장보기 목록", "🛒"),
]
CUISINES = ["전체", core.QUICK_LABEL, "한식", "양식", "중식", "일식", "분식", "기타"]
CATEGORY_EMOJI = {
    "간편식": "🍱",
    "채소류": "🥬", "과일류": "🍎", "콩류": "🫘", "육류": "🥩", "수산물": "🐟", "달걀류": "🥚", "두부류": "🧈",
    "유제품": "🥛", "곡류": "🍚", "면류": "🍜", "빵류": "🍞", "가루류": "🌾", "가공식품": "🥫", "냉동식품": "❄️",
    "반찬류": "🥢", "견과류": "🥜", "양념류": "🧄", "소스류": "🍯", "향신료": "🌿", "조미료": "🧂",
}
# 재고 관리 화면의 재료 고르기 탭 (분류를 묶어서 탭 수를 줄임)
PICKER_TABS = [
    ("🍱 간편식·냉동", ["간편식", "냉동식품"]),
    ("🥬 채소·과일", ["채소류", "과일류", "콩류"]),
    ("🥩 고기·해산물", ["육류", "수산물"]),
    ("🥚 달걀·유제품", ["달걀류", "두부류", "유제품"]),
    ("🍚 밥·면·빵", ["곡류", "면류", "빵류", "가루류"]),
    ("🥫 가공·반찬", ["가공식품", "반찬류", "견과류"]),
    ("🧄 양념·소스", ["양념류", "소스류", "조미료", "향신료"]),
]


# ─────────────────────────────── 데이터 (한 번만 읽고 캐시) ───────────────────────────────
@st.cache_data
def get_data():
    ingredients = core.load_ingredients()
    recipes = core.load_recipes()
    substitutes = core.load_substitutes()
    price_map = dict(zip(ingredients["name"], ingredients["price"]))
    category_map = dict(zip(ingredients["name"], ingredients["category"]))
    return ingredients, recipes, substitutes, price_map, category_map


# ─────────────────────────────── 사용자 상태 ───────────────────────────────
def init_state():
    """처음 접속하면 냉장고와 장보기 목록은 비어 있는 상태로 시작한다.
    상태는 이번 접속(브라우저 탭) 동안만 유지된다."""
    if st.session_state.get("_ready"):
        return
    ingredients, *_ = get_data()
    st.session_state.inventory = []
    st.session_state.basics = ingredients.loc[ingredients["basic"], "name"].tolist()
    st.session_state.cart = []
    st.session_state.checked = []
    st.session_state.cuisine = "전체"
    st.session_state._ready = True


def owned():
    """보유 재료 = 내 냉장고 + 체크해 둔 기본 재료"""
    return set(st.session_state.inventory) | set(st.session_state.basics)


def toggle_inventory(name):
    inv = st.session_state.inventory
    inv.remove(name) if name in inv else inv.append(name)


def toggle_cart(rid):
    cart = st.session_state.cart
    cart.remove(rid) if rid in cart else cart.append(rid)


def shopping_list():
    _, recipes, _, price_map, _ = get_data()
    return core.create_shopping_list(recipes, st.session_state.cart, owned(), price_map)


# ─────────────────────────────── 디자인 ───────────────────────────────
CSS = """
<style>
@font-face{font-family:'GmarketSans';font-weight:300;font-display:swap;src:url('/app/static/GmarketSansLight.woff') format('woff'),url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansLight.woff') format('woff')}
@font-face{font-family:'GmarketSans';font-weight:500;font-display:swap;src:url('/app/static/GmarketSansMedium.woff') format('woff'),url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff')}
@font-face{font-family:'GmarketSans';font-weight:700;font-display:swap;src:url('/app/static/GmarketSansBold.woff') format('woff'),url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff')}
:root{--green:#4F7D3A;--green-dk:#355E24;--green-soft:#E2EFD6;--orange:#F28A2E;--orange-dk:#A9500F;--orange-soft:#FDE7D1;
      --fg:#1E211B;--muted:#5C6056;--line:#D8D6CA;--bg:#F6F6F1;--sand:#F3EBD2}
html,body,.stApp,.stMarkdown,button,input,textarea,select,label,p,li,[data-testid="stMetricValue"]{
  font-family:'GmarketSans','Apple SD Gothic Neo','Malgun Gothic',sans-serif!important}
.stApp{background:var(--bg)}
header[data-testid="stHeader"]{background:transparent;height:0}
/* 작업 영역: 넓게, 좌우 여백 넉넉히 */
.block-container{max-width:1480px;padding:2.2rem 3rem 4rem}
h1,h2,h3{font-weight:700!important;letter-spacing:-.03em;color:var(--fg)}
/* 왼쪽 고정 메뉴 */
section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
/* 컴퓨터·태블릿: 왼쪽 메뉴를 고정으로 펼쳐 둔다 (모바일에서는 기본 햄버거 메뉴로 접힘) */
@media (min-width:768px){
  section[data-testid="stSidebar"]{width:264px!important;min-width:264px!important}
  [data-testid="stSidebarCollapseButton"]{display:none!important}
}
/* 모바일 */
@media (max-width:767px){
  .block-container{padding:1rem 1rem 3rem}
  .nt-head{padding:1.1rem 1rem;border-radius:0}
  .nt-head{flex-direction:column;align-items:flex-start;gap:.8rem}
  .nt-title{font-size:1.5rem}
  .nt-kpis{width:100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}
  .nt-kpi{min-width:0;padding:.45rem .6rem}.nt-kpi b{font-size:1.15rem}
  .nt-thumb{height:110px;font-size:46px}
}
section[data-testid="stSidebar"] .block-container,section[data-testid="stSidebarUserContent"]{padding-top:1.4rem}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a{padding:.55rem .8rem;border-radius:0;margin:2px 0}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover{background:#F3F3EE}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]{background:var(--green)}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] p,section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] p{color:#fff;font-weight:700}
section[data-testid="stSidebar"] [data-testid="stPageLink"] p{font-size:1rem;font-weight:500}
.nt-side-stat{display:flex;justify-content:space-between;padding:.45rem .2rem;border-bottom:1px dashed var(--line);font-size:.92rem}
.nt-side-stat b{font-weight:700}
.nt-side-stat.g b{color:var(--green-dk)}.nt-side-stat.o b{color:var(--orange-dk)}
.nt-side-label{font-size:.75rem;color:var(--muted);letter-spacing:.04em;margin:1.4rem 0 .3rem}
/* 페이지 머리 */
.nt-head{position:relative;overflow:hidden;display:flex;align-items:flex-end;justify-content:space-between;gap:2rem;margin-bottom:1.3rem;padding:1.7rem 2rem;border-radius:0;
  background:linear-gradient(118deg,#DCEDCB 0%,#EEF1DC 48%,#FBE6CF 100%);border:1px solid #CFE0BF}
.nt-head::before{content:"";position:absolute;right:-60px;top:-90px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(242,138,46,.22),transparent 68%)}
.nt-head>*{position:relative;z-index:1}
.nt-hand{color:var(--orange-dk);font-weight:700;font-size:.95rem;margin-bottom:.15rem}
.nt-title{font-size:2rem;font-weight:700;letter-spacing:-.035em;line-height:1.2}
.nt-sub{color:var(--muted);font-weight:300;margin-top:.3rem;font-size:.98rem}
.nt-kpis{display:flex;gap:.6rem}
.nt-kpi{background:rgba(255,255,255,.92);border-radius:0;padding:.65rem 1.1rem;min-width:124px;box-shadow:0 4px 14px rgba(53,94,36,.10)}
.nt-kpi span{display:block;font-size:.75rem;color:var(--muted)}
.nt-kpi b{font-size:1.45rem;font-weight:700;letter-spacing:-.02em}
.nt-kpi.g b{color:var(--green-dk)}.nt-kpi.o b{color:var(--orange-dk)}
/* 패널 제목 */
.nt-ph{font-weight:700;font-size:1.1rem;margin:.1rem 0 .6rem;display:flex;align-items:baseline;gap:.5rem}
.nt-ph small{font-weight:300;color:var(--muted);font-size:.85rem}
.nt-label{font-size:.8rem;color:var(--muted);margin:.7rem 0 .25rem;letter-spacing:.02em}
.nt-fine{font-size:.78rem;color:var(--muted);font-weight:300}
.nt-empty{text-align:center;color:var(--muted);font-weight:300;padding:2.2rem 1rem;line-height:1.7}
.nt-empty .big{font-size:2.6rem;display:block}
/* 레시피 카드 */
.nt-thumb{position:relative;height:132px;border-radius:0;display:flex;align-items:center;justify-content:center;font-size:58px;margin-bottom:.55rem}
.nt-t0{background:var(--green-soft)}.nt-t1{background:var(--orange-soft)}.nt-t2{background:var(--sand)}
.nt-badge{position:absolute;left:8px;top:8px;padding:3px 9px;border-radius:0;font-size:12px;font-weight:700;color:#fff}
.nt-b0{background:var(--green)}.nt-b1{background:var(--orange)}.nt-b2{background:#444}
.nt-qtag{position:absolute;left:8px;bottom:8px;font-size:11px;font-weight:700;color:#fff;background:#C2611A;padding:2px 7px}
.nt-ctag{position:absolute;right:8px;top:8px;font-size:11px;color:var(--muted);background:#fff;padding:2px 7px;border-radius:0}
.nt-name{font-weight:700;font-size:1.04rem;letter-spacing:-.02em;margin:.1rem 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nt-miss{font-size:.84rem;color:var(--muted);height:1.35rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nt-miss b{color:var(--orange-dk);font-weight:500}
.nt-cost{font-weight:700;font-size:.95rem;margin:.15rem 0 .35rem}
.nt-cost.zero{color:var(--green)}
/* 추천 구역 머리 */
.nt-group{display:flex;align-items:center;gap:.6rem;padding:.65rem 1rem;border-radius:0;margin:1.8rem 0 .9rem;font-weight:700;font-size:1.05rem}
.nt-group em{font-style:normal;font-weight:300;font-size:.85rem;opacity:.85}
.nt-group span{margin-left:auto;font-weight:500;font-size:.85rem}
.nt-g0{background:var(--green-soft);color:var(--green-dk);border-left:5px solid var(--green)}.nt-g1{background:var(--orange-soft);color:var(--orange-dk);border-left:5px solid var(--orange)}.nt-g2,.nt-g3{background:#E9E8DF;color:var(--fg);border-left:5px solid #9A9C92}
/* 재료 태그 */
.nt-tags{display:flex;flex-wrap:wrap;gap:6px;margin:.2rem 0 .5rem}
.nt-tag{padding:5px 11px;border-radius:0;font-size:.9rem;background:#EFEEE7}
.nt-tag.have{background:var(--green-soft);color:var(--green-dk)}
.nt-tag.miss{background:var(--orange-soft);color:var(--orange-dk)}
/* 장보기 표 */
.nt-th{font-size:.78rem;color:var(--muted);padding:.3rem 0;border-bottom:1px solid var(--line)}
.nt-total{font-size:2.2rem;font-weight:700;letter-spacing:-.03em;margin:.1rem 0}
/* 버튼 */
.stButton button{border-radius:0}
button[kind="primary"]{background:var(--green)!important;border-color:var(--green)!important;color:#fff!important}
button[kind="primary"]:hover{background:var(--green-dk)!important}
.stTabs [data-baseweb="tab"]{font-weight:500}
/* 모든 상자를 각지게 (Streamlit 기본 요소 포함) */
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stContainer"],.stButton button,[data-testid="stPageLink"] a,
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="base-input"],.stTextInput input,[data-baseweb="popover"],
[data-baseweb="tab-list"],[data-baseweb="checkbox"] span,div[role="dialog"],[data-testid="stAlert"],[data-testid="stToast"],img{border-radius:0!important}

/* ── 라이트 모드 고정: 사용자 기기가 다크 모드여도, 설정 파일이 없어도 글자·버튼이 잘 보이게 ── */
.stApp,.stApp p,.stApp li,.stApp label,.stApp span,.stApp h1,.stApp h2,.stApp h3,.stApp h4,
[data-testid="stMarkdownContainer"],[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"]{color:var(--fg)}
[data-testid="stCaptionContainer"],.nt-sub,.nt-fine,.nt-label,.nt-ph small{color:var(--muted)!important}
.nt-hand{color:var(--orange-dk)!important}
.nt-kpi.g b{color:var(--green-dk)!important}.nt-kpi.o b{color:var(--orange-dk)!important}
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div{background:#fff!important}
section[data-testid="stSidebar"] *{color:var(--fg)}
[data-testid="stSidebarNav"]{display:none!important}
.stButton button[kind="secondary"],.stButton button[kind="tertiary"],[data-testid="stBaseButton-secondary"]{background:#fff!important;color:var(--fg)!important;border:1px solid #CFCDBF!important}
.stButton button[kind="secondary"]:hover,[data-testid="stBaseButton-secondary"]:hover{border-color:var(--green)!important;color:var(--green-dk)!important}
.stButton button[kind="secondary"] p,[data-testid="stBaseButton-secondary"] p{color:inherit!important}
.stButton button[kind="primary"] p,[data-testid="stBaseButton-primary"] p{color:#fff!important}
[data-testid="stBaseButton-primary"]{background:var(--green)!important;border-color:var(--green)!important;color:#fff!important}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="base-input"],.stTextInput input{background:#fff!important;color:var(--fg)!important;border-color:#CFCDBF!important}
[data-baseweb="select"] *,.stTextInput input::placeholder{color:var(--muted)!important}
[data-baseweb="popover"] ul,[data-baseweb="menu"],[role="listbox"]{background:#fff!important}
[role="option"]{color:var(--fg)!important}[role="option"]:hover{background:var(--green-soft)!important}
.stTabs [data-baseweb="tab"] p{color:var(--muted)}
.stTabs [aria-selected="true"] p{color:var(--green-dk)!important;font-weight:700}
.stTabs [data-baseweb="tab-highlight"]{background:var(--green)!important}
.stTabs [data-baseweb="tab-border"]{background:var(--line)!important}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important}
[data-baseweb="checkbox"] [aria-checked="true"],[data-testid="stCheckbox"] input:checked+div{background:var(--green)!important;border-color:var(--green)!important}
[data-baseweb="radio"] [aria-checked="true"]>div:first-child{background:var(--green)!important;border-color:var(--green)!important}
div[role="dialog"]{background:#fff!important}
[data-testid="stMetricValue"]{color:var(--fg)}

/* 모든 글자에 G마켓 산스 적용 (Streamlit 아이콘 글꼴은 제외) */
.stApp *:not([data-testid="stIconMaterial"]):not(.material-icons):not(code):not(pre),
[data-baseweb="tooltip"] *,[data-baseweb="popover"] *{font-family:'GmarketSans','Apple SD Gothic Neo','Malgun Gothic',sans-serif!important}
/* 말줄임된 이름에 마우스를 올리면 뜨는 풍선: 흰 바탕 + 진한 글자 */
[data-baseweb="tooltip"],[data-baseweb="tooltip"]>div,[data-testid="stTooltipContent"],[data-testid="stTooltipHoverTarget"] + div{
  background:#fff!important;color:var(--fg)!important;border:1px solid var(--line)!important;border-radius:0!important;box-shadow:0 6px 18px rgba(30,40,20,.15)!important}
[data-baseweb="tooltip"] *,[data-testid="stTooltipContent"] *{background:transparent!important;color:var(--fg)!important}
</style>
"""


def setup(title):
    """모든 페이지 맨 위에서 호출: 상태 준비, 디자인, 왼쪽 메뉴. (페이지 설정은 app.py에서 한 번만)"""
    init_state()
    st.markdown(CSS, unsafe_allow_html=True)
    _sidebar()


def _sidebar():
    _, recipes, _, price_map, _ = get_data()
    ranked = core.recommend_recipes(recipes, owned(), price_map)
    items = shopping_list()
    with st.sidebar:
        if LOGO.exists():
            st.image(str(LOGO), width=190)
        st.markdown('<div class="nt-side-label">메뉴</div>', unsafe_allow_html=True)
        for path, label, icon in PAGES:
            st.page_link(path, label=label, icon=icon)
        st.markdown('<div class="nt-side-label">지금 내 상황</div>', unsafe_allow_html=True)
        n_now = int((ranked["missing_count"] == 0).sum()) if st.session_state.inventory else 0
        st.markdown(
            f'<div class="nt-side-stat"><span>냉장고 재료</span><b>{len(st.session_state.inventory)}개</b></div>'
            f'<div class="nt-side-stat g"><span>바로 만들 수 있는 메뉴</span><b>{n_now}개</b></div>'
            f'<div class="nt-side-stat o"><span>장보기 재료</span><b>{len(items)}개</b></div>'
            f'<div class="nt-side-stat"><span>예상 장보기 비용</span><b>{core.won(sum(x["price"] for x in items))}</b></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="nt-fine" style="margin-top:1.6rem">가격은 실시간 판매가가 아닌 자체 기준가격입니다.</p>',
                    unsafe_allow_html=True)


def page_head(hand, title, sub="", kpis=()):
    """페이지 머리: 왼쪽 제목, 오른쪽 요약 숫자. kpis = [(이름, 값, 'g'|'o'|''), ...]"""
    kpi_html = "".join(f'<div class="nt-kpi {c}"><span>{n}</span><b>{v}</b></div>' for n, v, c in kpis)
    st.markdown(
        f'<div class="nt-head"><div><div class="nt-hand">{hand}</div><div class="nt-title">{title}</div>'
        f'{f"<div class=nt-sub>{sub}</div>" if sub else ""}</div><div class="nt-kpis">{kpi_html}</div></div>',
        unsafe_allow_html=True,
    )


def panel_title(text, small=""):
    st.markdown(f'<div class="nt-ph">{text}<small>{small}</small></div>', unsafe_allow_html=True)


def empty(icon, text):
    st.markdown(f'<div class="nt-empty"><span class="big">{icon}</span>{text}</div>', unsafe_allow_html=True)


# ─────────────────────────────── 레시피 카드 · 상세 ───────────────────────────────
def thumb_html(row, show_badge=True, height=None):
    """음식 이미지 자리 (사진이 없을 때 이모지)."""
    tint = f"nt-t{int(str(row['recipe_id'])[1:]) % 3}"
    badge = ""
    if show_badge and "missing_count" in row:
        k = min(int(row["missing_count"]), 2)
        text = "100% 보유" if k == 0 else f"+{int(row['missing_count'])}개 필요"
        badge = f'<span class="nt-badge nt-b{k}">{text}</span>'
    style = f' style="height:{height}px;font-size:{int(height * .45)}px"' if height else ""
    qtag = '<span class="nt-qtag">🍱 간편식 활용</span>' if row.get("quick") else ""
    return f'<div class="nt-thumb {tint}"{style}>{badge}<span class="nt-ctag">{row["cuisine"]}</span>{qtag}{row["emoji"]}</div>'


def recipe_card(row, key):
    """추천 화면의 메뉴 카드 한 장 (이미지·이름·부족 재료·추가 비용·버튼)."""
    rid = row["recipe_id"]
    with st.container(border=True):
        photo = BASE_DIR / str(row.get("image", ""))
        if photo.is_file():   # images/R001.jpg 같은 실제 사진이 있으면 사진을 쓴다
            st.image(str(photo), use_container_width=True)
        else:
            st.markdown(thumb_html(row), unsafe_allow_html=True)
        miss = ", ".join(row["missing"])
        miss_html = f"부족: <b>{miss}</b>" if miss else f"보유 재료 {row['own_rate']}%"
        cost = row["extra_cost"]
        st.markdown(
            f'<div class="nt-name" title="{row["name"]}">{row["name"]}</div>'
            f'<div class="nt-miss" title="{miss}">{miss_html}</div>'
            f'<div class="nt-cost {"" if cost else "zero"}">추가 비용 {"약 " + core.won(cost) if cost else "0원"}</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("상세보기", key=f"{key}-d-{rid}", use_container_width=True):
            show_detail(rid)
        if row["missing_count"]:
            in_cart = rid in st.session_state.cart
            c2.button("✓ 담음" if in_cart else "장보기 +", key=f"{key}-c-{rid}", use_container_width=True,
                      type="primary" if in_cart else "secondary", on_click=toggle_cart, args=(rid,),
                      help="장보기 목록에서 빼기" if in_cart else "부족 재료를 장보기 목록에 담기")


def tags(items, kind=""):
    if not items:
        return '<div class="nt-tags"><span class="nt-fine">없음</span></div>'
    mark = {"have": "✓ ", "miss": "✕ "}.get(kind, "")
    return '<div class="nt-tags">' + "".join(f'<span class="nt-tag {kind}">{mark}{x}</span>' for x in items) + "</div>"


def render_compare(rid, key):
    """메뉴 상세 / 검색 결과의 재료 비교 화면 (명세서 11·13번).
    넓은 화면에 맞게 왼쪽은 재료 비교·비용·대체 재료, 오른쪽은 조리법."""
    _, recipes, substitutes, price_map, _ = get_data()
    row = recipes.set_index("recipe_id").loc[rid]
    own = owned()
    have, missing = core.compare_ingredients(row["ingredients"], own)
    cost = core.calculate_extra_cost(missing, price_map)

    top_l, top_r = st.columns([1, 4], vertical_alignment="center")
    top_l.markdown(thumb_html({**row.to_dict(), "recipe_id": rid}, show_badge=False, height=110), unsafe_allow_html=True)
    with top_r:
        st.markdown(f"### {row['name']}")
        status = f":orange[**+{len(missing)}개 필요 · 예상 추가비용 약 {core.won(cost)}**]" if missing \
            else ":green[**지금 바로 만들 수 있어요**]"
        st.markdown(f"{row['cuisine']} · 재료 {len(row['ingredients'])}개 &nbsp;|&nbsp; {status}")

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown('<div class="nt-label">필요한 재료</div>' + tags(row["ingredients"]), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown('<div class="nt-label">현재 보유</div>' + tags(have, "have"), unsafe_allow_html=True)
        c2.markdown('<div class="nt-label">부족</div>' + tags(missing, "miss"), unsafe_allow_html=True)
        subs = core.find_substitutes(substitutes, missing)
        if len(subs):
            st.markdown('<div class="nt-label">대체 가능 재료</div>', unsafe_allow_html=True)
            for _, s in subs.iterrows():
                mine = " · :green[**보유 중**]" if s["substitute"] in own else ""
                st.markdown(f"- **{s['original']} → {s['substitute']}**{mine}  \n  :gray[{s['usage']} · {s['note']}]")
    with right:
        st.markdown('<div class="nt-label">간단한 조리법</div>', unsafe_allow_html=True)
        st.markdown("\n".join(f"{i}. {step}" for i, step in enumerate(row["steps"], 1)))
        if missing:
            in_cart = rid in st.session_state.cart
            st.button("✓ 장보기 목록에 담았어요 (누르면 빼기)" if in_cart else "부족 재료 장보기 목록에 추가",
                      key=f"{key}-cart-{rid}", type="secondary" if in_cart else "primary",
                      use_container_width=True, on_click=toggle_cart, args=(rid,))


@st.dialog("메뉴 상세", width="large")
def show_detail(rid):
    render_compare(rid, key="dlg")
