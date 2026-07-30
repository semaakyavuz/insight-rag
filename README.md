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

## Local development setup

1. `.env` dosyanı oluştur:

   ```bash
   cp .env.example .env
   ```

2. pgvector destekli Postgres'i ayağa kaldır:

   ```bash
   docker-compose up -d
   ```

   Bu, `pgvector/pgvector:pg16` imajıyla `5432` portunda bir Postgres servisi başlatır ve verileri `postgres_data` volume'ünde kalıcı tutar.

3. Bağımlılıkları kur ve migration'ları uygula:

   ```bash
   pip install -r requirements.txt
   alembic upgrade head
   ```

4. Uygulamayı çalıştır:

   ```bash
   uvicorn app.main:app --reload
   ```

## Proje Yapısı

```
app/
  api/       # API route tanımları
  services/  # İş mantığı
  models/    # Veri modelleri
tests/       # Test dosyaları
```
