FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code into the container
COPY . .

# NOTE: Since your model is located in '../ml-model/models/best_model.pth' in the 
# original repo, make sure to copy that model into a 'models' folder inside 'backend' 
# BEFORE uploading to Hugging Face, or adjust the path accordingly.
# COPY models/best_model.pth /app/models/best_model.pth

# Hugging Face Spaces expects the app to run on port 7860
EXPOSE 7860

# Command to run the FastAPI application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
