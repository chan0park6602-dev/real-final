"""냉털메이트 핵심 로직 (명세서 18번 함수).

Streamlit에 의존하지 않는 순수 함수만 모아 두었다.
화면 코드(app.py, pages/)는 이 함수들을 불러서 쓴다.
"""
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
QUICK_CATEGORIES = ("간편식", "냉동식품")   # 우리 서비스의 핵심: 간편식·냉동식품을 활용한 요리
QUICK_LABEL = "🍱 간편식 활용"
DATA_DIR = BASE_DIR / "data"


# ─────────────────────────────── 데이터 불러오기 ───────────────────────────────
def load_ingredients(path=DATA_DIR / "ingredients.csv"):
    """식재료와 가격 데이터 불러오기.

    반환: DataFrame (ingredient_id, name, category, price, basic[bool])
    """
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["name"] = df["name"].astype(str).str.strip()
    df["price"] = df["price"].astype(int)
    df["basic"] = df["basic"].astype(str).str.upper().eq("Y")
    return df


def load_recipes(path=DATA_DIR / "recipes.csv"):
    """레시피 데이터 불러오기.

    ingredients, steps 열은 '|'로 구분된 문자열이므로 리스트로 바꿔 둔다.
    반환: DataFrame (recipe_id, name, cuisine, ingredients[list], steps[list], image, emoji)
    """
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["ingredients"] = df["ingredients"].astype(str).apply(lambda s: [x.strip() for x in s.split("|") if x.strip()])
    df["steps"] = df["steps"].fillna("").astype(str).apply(lambda s: [x.strip() for x in s.split("|") if x.strip()])
    df["emoji"] = [pick_emoji(n, c) for n, c in zip(df["name"], df["cuisine"])]
    # 간편식·냉동식품이 하나라도 들어가면 '간편식 활용' 레시피로 표시
    ing = load_ingredients()
    quick = set(ing.loc[ing["category"].isin(QUICK_CATEGORIES), "name"])
    df["quick"] = df["ingredients"].apply(lambda ings: any(x in quick for x in ings))
    return df


def load_substitutes(path=DATA_DIR / "substitutes.csv"):
    """대체 식재료 불러오기. 반환: DataFrame (original, substitute, usage, note)"""
    return pd.read_csv(path, encoding="utf-8-sig").fillna("")


# ─────────────────────────────── 재료 비교 ───────────────────────────────
def compare_ingredients(recipe_ingredients, owned):
    """현재 재고와 특정 레시피 비교.

    recipe_ingredients: 레시피에 필요한 재료 리스트
    owned: 사용자가 가진 재료 집합 (기본 재료 포함)
    반환: (보유 재료 리스트, 부족 재료 리스트)
    """
    owned = set(owned)
    have = [x for x in recipe_ingredients if x in owned]
    missing = [x for x in recipe_ingredients if x not in owned]
    return have, missing


def find_missing_ingredients(recipe_ingredients, owned):
    """부족 재료 추출: 필요한 재료 - 현재 재고"""
    return compare_ingredients(recipe_ingredients, owned)[1]


def calculate_extra_cost(missing, price_map):
    """부족 재료의 대표 가격 합산"""
    return int(sum(price_map.get(x, 0) for x in missing))


# ─────────────────────────────── 추천 ───────────────────────────────
def recommend_recipes(recipes, owned, price_map, cuisine=None):
    """모든 레시피에 대해 부족 재료를 계산하고 정렬한다.

    정렬 기준
      1순위: 부족 재료 수 (적은 순)
      2순위: 예상 추가 구매 비용 (낮은 순)
      3순위: 필요한 재료 수 (많은 순 → 가진 재료를 더 많이 쓰는 메뉴 먼저)
    반환: DataFrame (원래 열 + have, missing, missing_count, extra_cost, own_rate)
    """
    if cuisine in (None, "전체"):
        df = recipes
    elif cuisine == QUICK_LABEL:
        df = recipes[recipes["quick"]]
    else:
        df = recipes[recipes["cuisine"] == cuisine]
    df = df.copy()
    pairs = [compare_ingredients(ings, owned) for ings in df["ingredients"]]
    df["have"] = [p[0] for p in pairs]
    df["missing"] = [p[1] for p in pairs]
    df["missing_count"] = df["missing"].apply(len)
    df["extra_cost"] = df["missing"].apply(lambda m: calculate_extra_cost(m, price_map))
    df["need_count"] = df["ingredients"].apply(len)
    df["own_rate"] = (df["have"].apply(len) / df["need_count"] * 100).round().astype(int)
    return df.sort_values(["missing_count", "extra_cost", "need_count"], ascending=[True, True, False]).reset_index(drop=True)


def search_recipe(recipes, query):
    """메뉴 이름 검색 (공백 무시). 재료 이름과 정확히 같으면 그 재료가 들어간 메뉴도 찾는다."""
    q = re.sub(r"\s", "", str(query or ""))
    if not q:
        return recipes
    by_name = recipes["name"].str.replace(r"\s", "", regex=True).str.contains(q, regex=False)
    by_ing = recipes["ingredients"].apply(lambda ings: q in ings)
    return recipes[by_name | by_ing]


def find_substitutes(substitutes, missing):
    """부족 재료의 대체 식재료 검색"""
    return substitutes[substitutes["original"].isin(list(missing))]


def create_shopping_list(recipes, selected_ids, owned, price_map):
    """선택한 레시피들의 부족 재료를 하나로 모은다.

    같은 재료가 여러 메뉴에 필요해도 한 번만 넣는다 (수량 합산 없음).
    반환: [{"name": 재료, "price": 가격, "for": [메뉴 이름들]}, ...]
    """
    items = {}
    by_id = recipes.set_index("recipe_id")
    for rid in selected_ids:
        if rid not in by_id.index:
            continue
        row = by_id.loc[rid]
        for ing in find_missing_ingredients(row["ingredients"], owned):
            items.setdefault(ing, []).append(row["name"])
    return [{"name": k, "price": int(price_map.get(k, 0)), "for": v} for k, v in items.items()]


# ─────────────────────────────── 기타 ───────────────────────────────
_EMOJI_RULES = [
    (r"파스타|스파게티|알리오|까르보|봉골레", "🍝"), (r"피자", "🍕"), (r"타코|부리또|퀘사디아|나초", "🌮"),
    (r"샌드위치|버거", "🥪"), (r"라면|우동|국수|소바|면|팟타이|짬뽕|쌀국수", "🍜"), (r"카레", "🍛"),
    (r"주먹밥|오니기리|김밥|유부초밥", "🍙"), (r"만두|딤섬", "🥟"), (r"죽|수프|스프|오트밀", "🥣"),
    (r"샐러드", "🥗"), (r"새우", "🍤"), (r"연어|사케|참치|고등어|생선|명란|꽁치", "🐟"),
    (r"닭|치킨|오야코", "🍗"), (r"제육|불고기|스테이크|돼지|소고기|함박|갈비|삼겹|규동|돈가스|돈까스|가츠", "🍖"),
    (r"찌개|탕|국|전골|나베|스튜", "🍲"), (r"전$|부침|팬케이크|오코노미", "🥞"), (r"토스트|산도|빵", "🍞"),
    (r"떡볶이|떡꼬치|어묵", "🍢"), (r"계란|달걀|에그|오믈렛", "🍳"), (r"밥|덮밥|동$|리조또", "🍚"),
    (r"감자", "🥔"), (r"토마토", "🍅"), (r"버섯", "🍄"), (r"나물|무침|볶음", "🥬"),
]
_CUISINE_EMOJI = {"한식": "🥘", "양식": "🍽️", "중식": "🥡", "일식": "🍱", "분식": "🍢"}


def pick_emoji(name, cuisine):
    """음식 사진이 없을 때 쓸 이모지 (메뉴 이름으로 추정)"""
    for pattern, emoji in _EMOJI_RULES:
        if re.search(pattern, str(name)):
            return emoji
    return _CUISINE_EMOJI.get(cuisine, "🍽️")


def won(n):
    """15000 → '15,000원'"""
    return f"{int(n):,}원"
