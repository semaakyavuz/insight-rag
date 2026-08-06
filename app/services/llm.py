from functools import lru_cache

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL_NAME

SYSTEM_PROMPT = (
    "Sana bir soru ve bu soruyla ilgili olabilecek bağlam parçaları verilecek. "
    "Yalnızca bu bağlamda yer alan bilgilere dayanarak cevap ver. "
    "Bağlamda yeterli bilgi yoksa bunu açıkça ve dürüstçe belirt; "
    "bağlamda olmayan hiçbir bilgiyi uydurma veya varsayma."
)


@lru_cache(maxsize=1)
def get_client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    user_prompt = f"Bağlam:\n{context}\n\nSoru: {question}"

    response = get_client().chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
