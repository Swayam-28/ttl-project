# Step 1: Start from an official lightweight Python image
FROM python:3.11-slim

# Install Git and Docker CLI to enable Docker-in-Docker orchestration
RUN apt-get update && \
    apt-get install -y git ca-certificates curl && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy dependencies file first (helps Docker cache layers efficiently)
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the app code
COPY . .

# Step 6: Tell Docker which port the app will run on
EXPOSE 5000

# Step 7: Start the app using gunicorn (production server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]