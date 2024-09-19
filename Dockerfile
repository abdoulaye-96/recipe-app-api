FROM python:3.9-alpine3.13
LABEL maintainer="abdoulaye02"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user 

ENV PATH="/py/bin:$PATH"

USER django-user



# FROM python:3.9-alpine3.13
# LABEL maintainer="abdoulaye02"

# ENV PYTHONUNBUFFERED=1

# # Install necessary system dependencies for Python and common libraries
# RUN apk add --no-cache \
#     gcc \
#     musl-dev \
#     libffi-dev \
#     openssl-dev \
#     python3-dev \
#     linux-headers \
#     jpeg-dev \
#     zlib-dev \
#     postgresql-dev \
#     mariadb-dev

# # Create virtual environment and upgrade pip
# RUN python -m venv /py && \
#     /py/bin/pip install --upgrade pip

# # Copy requirements and install Python dependencies
# COPY ./requirements.txt /tmp/requirements.txt
# RUN /py/bin/pip install -r /tmp/requirements.txt && rm -rf /tmp

# # Copy app code to /app
# COPY ./app /app
# WORKDIR /app

# # Expose the application port
# EXPOSE 8000

# # Add a non-root user
# RUN adduser --disabled-password --no-create-home django-user

# # Set virtual environment in PATH
# ENV PATH="/py/bin:$PATH"

# # Switch to non-root user
# USER django-user


