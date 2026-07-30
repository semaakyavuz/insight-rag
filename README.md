# insight-rag

FastAPI tabanlı bir Retrieval-Augmented Generation (RAG) servisi.

## Kurulum

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
uvicorn app.main:app --reload
```

Servis ayakta olduğunda `/health` endpoint'i üzerinden durum kontrolü yapılabilir.

## Docker

```bash
docker build -t insight-rag .
docker run -p 8000:8000 insight-rag
```

## Proje Yapısı

```
app/
  api/       # API route tanımları
  services/  # İş mantığı
  models/    # Veri modelleri
tests/       # Test dosyaları
```
