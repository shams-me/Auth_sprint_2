FROM python:3.11

WORKDIR /app/tests

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN sed -i 's/\r$//' entrypoint.sh
RUN chmod +x entrypoint.sh


ENV PYTHONPATH=/app/tests

CMD ["sh", "entrypoint.sh"]