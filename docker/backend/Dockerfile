FROM python:3.11.9-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY pyproject.toml uv.lock /code/
RUN pip install --upgrade pip && \
    pip install uv
COPY .env.example /code/.env
COPY ./ /code
RUN uv sync --frozen --no-dev
RUN chmod +x /code/docker/backend/entrypoint.sh

EXPOSE 8241 5555

ENTRYPOINT ["/code/docker/backend/entrypoint.sh"]