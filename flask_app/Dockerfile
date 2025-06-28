FROM python:3.9-slim

WORKDIR /app

# Install uv, the fast Python package installer
RUN pip install uv

# Copy the dependencies file to the working directory
COPY ./flask_app/requirements.txt .

# Install packages using uv
RUN uv pip install --no-cache -r requirements.txt --system

# Copy the rest of the application code
COPY ./flask_app/ .

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"] 