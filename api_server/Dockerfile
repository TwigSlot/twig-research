FROM python:3.9-slim-buster
RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip install gunicorn
RUN pip install poetry
COPY poetry.lock pyproject.toml /app/
WORKDIR /app
RUN poetry config virtualenvs.create false
RUN poetry install --without dev --no-interaction --no-ansi
RUN /usr/local/bin/python -m pip install "pymongo[srv]"
COPY api_server /app/api_server
WORKDIR /app
ENTRYPOINT [ "gunicorn" ]
CMD [ "-w", "4", "-b", "0.0.0.0:5000", "api_server.app:create_app()" ]