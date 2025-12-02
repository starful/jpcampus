FROM python:3.11-slim

WORKDIR /app

# 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 설정
ENV PORT=8080
ENV GCS_BUCKET_NAME=jpcampus

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]