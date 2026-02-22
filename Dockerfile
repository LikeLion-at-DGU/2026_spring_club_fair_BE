FROM python:3.11

WORKDIR /project
# 시스템 패키지 설치. requirements.txt를 활용한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# Gunicorn 활용 애플리케이션 실행
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]