from typing import Dict, List, Tuple
import json
import os
import re


def load_books() -> List[Dict]:
    base_dir = os.path.dirname(os.path.dirname(__file__))  # src klasörü
    data_path = os.path.join(base_dir, "data", "book.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    if not text:
        return ""
    mapping = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return str(text).translate(mapping).lower().strip()


def split_moods(raw: str) -> List[str]:
    raw_n = normalize(raw)
    if not raw_n:
        return []
    parts = [p.strip() for p in raw_n.split(",")]
    return [p for p in parts if p]


def contains_word(haystack: str, needle: str) -> bool:
    if not haystack or not needle:
        return False
    pattern = r"(?:^|\W)" + re.escape(needle) + r"(?:$|\W)"
    return re.search(pattern, haystack) is not None


def get_book_genres(book: Dict) -> List[str]:
    genres: List[str] = []

    if isinstance(book.get("genres"), list) and book["genres"]:
        for g in book["genres"]:
            g_n = normalize(g)
            if g_n:
                genres.append(g_n)

    if not genres:
        g1 = normalize(book.get("genre", ""))
        if g1:
            genres = [g1]

    return genres


def get_recommendations(profile: Dict[str, str], k: int = 3) -> List[Dict]:
    books = load_books()

    favorite_genre = normalize(profile.get("favorite_genre", ""))
    moods = split_moods(profile.get("mood", ""))
    last_book = normalize(profile.get("last_book", ""))

    def score_book(book: Dict) -> Tuple[float, Dict]:
        s = 0.0

        book_title = normalize(book.get("title", ""))
        book_author = normalize(book.get("author", ""))
        book_genres = get_book_genres(book)

        tags = [normalize(t) for t in (book.get("mood_tags", []) or [])]
        desc = normalize(book.get("description", ""))

        # 1) Tür eşleşmesi (genre + genres[])
        if favorite_genre and book_genres:
            if any(favorite_genre == g for g in book_genres):
                s += 4.0
            elif any(favorite_genre in g for g in book_genres):
                s += 3.0

        # 2) Mood eşleşmesi (çoklu)
        if moods:
            hit = 0
            for m in moods:
                if any(m in t for t in tags):
                    hit += 1
                if contains_word(desc, m):
                    s += 0.5
            s += hit * 2.0

        # 3) Tag zenginliği küçük bonus
        s += min(len(tags), 6) * 0.1

        # 4) last_book ile aynı kitabı önermeme
        if last_book and book_title:
            if last_book == book_title:
                s -= 100.0
            elif last_book in book_title or book_title in last_book:
                s -= 5.0

        meta = {
            "_score": s,
            "_author_n": book_author,
            "_genres_n": book_genres,
            "_title_n": book_title,
        }
        return s, {**book, **meta}

    scored = [score_book(b) for b in books]
    scored.sort(key=lambda x: x[0], reverse=True)

    candidates = [b for s, b in scored if s > 0] or [b for _, b in scored]

    # Çeşitlilik: aynı yazar / aynı tür yığılmasın (greedy)
    picked: List[Dict] = []
    used_authors = set()

    for _ in range(k):
        best = None
        best_val = -10**9

        for b in candidates:
            if any(p.get("id") == b.get("id") for p in picked):
                continue

            val = float(b.get("_score", 0.0))

            a = b.get("_author_n", "")
            if a and a in used_authors:
                val -= 1.5

            b_genres = b.get("_genres_n", []) or []
            if b_genres:
                same_genre_count = 0
                for p in picked:
                    p_genres = p.get("_genres_n", []) or []
                    if set(b_genres).intersection(set(p_genres)):
                        same_genre_count += 1
                if same_genre_count >= 2:
                    val -= 0.8

            if val > best_val:
                best_val = val
                best = b

        if not best:
            break

        picked.append(best)
        if best.get("_author_n"):
            used_authors.add(best["_author_n"])

    for b in picked:
        b.pop("_score", None)
        b.pop("_author_n", None)
        b.pop("_genres_n", None)
        b.pop("_title_n", None)

    return picked
