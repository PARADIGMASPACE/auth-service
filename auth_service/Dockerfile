FROM python:3.11

WORKDIR /auth_service

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH="/auth_service:/auth_service/app:/auth_service/backend"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]