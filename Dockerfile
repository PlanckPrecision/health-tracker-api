FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)

# Install latest setuptools and wheel to fix build error
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# Copy source
COPY . .

EXPOSE 5000

# Run database migrations then start gunicorn
CMD ["sh", "-c", "flask db upgrade && gunicorn -w 2 -b 0.0.0.0:5000 'main:app'"]
