FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# Instalar dependencias necesarias
RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Copiar el entorno virtual y el código
COPY --from=builder /app/.venv .venv/
COPY . .

# Configurar el PATH para usar el entorno virtual
ENV PATH="/app/.venv/bin:$PATH"

# Comando de inicio explícito
CMD ["python", "main.py"]
