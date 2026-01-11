# src/agents/explanation_agent.py

import os
from groq import Groq

def create_explanation(profile, recommendations):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    books_text = "\n".join(
        [f"- {book['title']} ({book['genre']})" for book in recommendations]
    )

    prompt = f"""
Sen bir kitap öneri uzmanısın.
Aşağıdaki KULLANICI PROFİLİ ve ÖNERİLEN KİTAPLAR bilgisine göre,
kullanıcıya NEDEN bu kitapları önerdiğini açıklayan samimi, düzgün TÜRKÇE bir metin yaz.

KULLANICI PROFİLİ:
- Ruh hali: {profile.get("mood")}
- Tercih ettiği tür: {profile.get("favorite_genre")}
- Okuma amacı: {profile.get("reading_goal")}
- En son okuduğu kitap: {profile.get("last_book")}

ÖNERİLEN KİTAPLAR:
{books_text}

YAZIM KURALLARI:
- SADECE TÜRKÇE yaz.
- Yazım hatalarından kaçınmaya çalış.
- İngilizce kelime kullanma.
- Kullanıcıya 'sen' diye hitap et.
- Cevabı MARKDOWN formatında yaz.

ÇIKTI FORMATIN:
1. Kısa ve sıcak bir giriş paragrafı
2. Her kitap için şu formatta yaz:
   ### Kitap Adı
   - Neden bu ruh haline uygun?
   - Neden bu türe uygun?
   - Kullanıcının okuma amacına nasıl yardımcı olur?
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
