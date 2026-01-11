# src/agents/profile_agent.py

from typing import Dict

def normalize(text: str) -> str:
    if not text:
        return ""
    mapping = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return text.translate(mapping).lower().strip()

def map_mood(raw_mood: str) -> str:
    mood = normalize(raw_mood)
    # Basit eş anlam grupları
    if mood in ["mutlu", "iyi", "neşeli", "neseli"]:
        return "mutlu"
    if mood in ["uzgun", "üzgün", "moralim bozuk", "kotu", "kötü"]:
        return "uzgun"
    if mood in ["heyecanli", "heyecanlı"]:
        return "heyecanli"
    if mood in ["stresli", "yorgun", "bitkin"]:
        return "stresli"
    return mood or "belirsiz"

def map_genre(raw_genre: str) -> str:
    genre = normalize(raw_genre)
    if "fant" in genre:  # fantastik / fantazi
        return "fantastik"
    if "bilim" in genre or "sci" in genre:
        return "bilim kurgu"
    if "distopya" in genre or "disto" in genre:
        return "distopya"
    return genre or "belirsiz"

def build_user_profile(user_input: Dict[str, str]) -> Dict[str, str]:
    """
    Kullanıcıdan gelen girdilere göre normalize edilmiş ve yorumlanmış profil oluşturur.
    """
    raw_mood = user_input.get("mood", "")
    raw_genre = user_input.get("genre", "")
    last_book = user_input.get("last_book", "").strip()

    mood = map_mood(raw_mood)
    favorite_genre = map_genre(raw_genre)

    # Basit bir okuma amacı çıkaralım (model tasarımı)
    if mood in ["uzgun", "stresli"]:
        reading_goal = "rahatlamak ve kafasini dagitmak"
    elif mood in ["mutlu", "heyecanli"]:
        reading_goal = "keyifli ve macerali bir seyler okumak"
    else:
        reading_goal = "farkli dunyalara gitmek"

    profile = {
        "mood": mood,
        "favorite_genre": favorite_genre,
        "last_book": last_book or "bilinmiyor",
        "reading_goal": reading_goal,
        "summary": f"Kullanici su an {mood} ruh halinde, {favorite_genre} turunu seviyor ve amaci {reading_goal}."
    }

    return profile
