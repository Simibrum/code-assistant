# Dockerfile to allow isolated development on different branches
FROM python:3.12.1-alpine

# Install git
RUN apk update && apk add --no-cache git

# Install gcc
RUN apk add --no-cache gcc musl-dev linux-headers

# Create a new directory for the application
RUN mkdir /agent

# Echo the repository URL and branch name
ARG REPO_URL
ARG BRANCH_NAME

# Clone the repository
RUN git clone ${REPO_URL} /agent
# Checkout the branch
RUN cd /agent && git checkout ${BRANCH_NAME}

# Set the working directory
WORKDIR /agent

# Install the requirements
RUN pip install -r requirements.txt

# Run the application
# CMD ["python", "app.py"]