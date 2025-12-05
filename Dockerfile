FROM python:3.11-slim

# 작업 디렉토리를 /code 로 변경 (폴더명 충돌 방지)
WORKDIR /code

# 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 소스 복사
COPY . .

# 포트 설정
ENV PORT=8080

# 실행 명령어 (app 패키지 실행)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]