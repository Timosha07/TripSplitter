FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
RUN useradd --create-home bot
USER bot
CMD ["sh", "-c", "python migrate.py && python bot.py"]
