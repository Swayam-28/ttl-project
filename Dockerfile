# Step 1: Start from an official lightweight Python image
FROM python:3.11-slim

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