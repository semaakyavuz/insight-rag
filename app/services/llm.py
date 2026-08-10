from functools import lru_cache

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL_NAME

SYSTEM_PROMPT = (
    "Sana bir soru ve bu soruyla ilgili olabilecek bağlam parçaları verilecek. "
    "Yalnızca bu bağlamda yer alan bilgilere dayanarak cevap ver. "
    "Bağlamda yeterli bilgi yoksa bunu açıkça ve dürüstçe belirt; "
    "bağlamda olmayan hiçbir bilgiyi uydurma veya varsayma. "
    "Kullanıcı 'basitleştir', 'özetle', 'madde madde anlat' gibi bir format "
    "veya sadeleştirme talebinde bulunursa, kaynak metnin teknik dilini, "
    "yapısını (tablo, algoritma adımları, akademik terimler) olduğu gibi "
    "kopyalama; içeriği gerçekten sade ve günlük dille yeniden ifade et. "
    "Teknik bir terim kullanman gerekiyorsa, yanına parantez içinde kısa "
    "bir açıklama ekle."
)


@lru_cache(maxsize=1)
def get_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def generate_answer(
    question: str,
    context_chunks: list[str],
    history: list[dict[str, str]] | None = None,
) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    user_prompt = f"Bağlam:\n{context}\n\nSoru: {question}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    response = get_client().chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=messages,
    )
    return response.choices[0].message.content
