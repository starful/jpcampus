FROM python:3.11-slim

WORKDIR /code

# 1. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 필수 앱 소스만 복사 (scripts, file 등 제외)
COPY app ./app
COPY build_data.py .

# 3. 빌드 시점에 Markdown -> JSON 변환 실행
# (app/content가 복사되었으므로 실행 가능)
RUN python build_data.py

# 4. 실행 설정
ENV PORT=8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]