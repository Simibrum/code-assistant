# Dockerfile to allow isolated development on different branches
FROM python:3.12.1-alpine

# Install git
RUN apk update && apk add --no-cache git

# Create a new directory for the application
RUN mkdir /app

# Echo the repository URL and branch name
ARG REPO_URL
ARG BRANCH_NAME

# Clone the repository
RUN git clone ${REPO_URL} /app
# Checkout the branch
RUN cd /app && git checkout ${BRANCH_NAME}

# Set the working directory
WORKDIR /app

# Install the requirements
RUN pip install -r requirements.txt

# Run the application
# CMD ["python", "app.py"]