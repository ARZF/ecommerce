FROM python:3.9-slim

WORKDIR /app

# Copy common requirements and install dependencies
COPY common/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared package (imported as `common.x` from the app dir)
COPY common/ ./common/

# Copy application code
COPY order_service/ .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

