FROM tiangolo/uvicorn-gunicorn-fastapi:latest

COPY ./requirements.txt /app/requirements.txt
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini
COPY ./prestart.sh /app/prestart.sh
RUN ssh-keygen -t rsa -b 4096 -m pem -f /app/private.pem -N zaer@2023
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app
