FROM python:3.9-alpine3.13
LABEL maintainer="ceewa30.com"

# don't want to buffered the output
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

COPY ./app /app
WORKDIR /app
EXPOSE 8000

# create a new virtual environment
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = 'true' ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # remove the temporary folder, don't want the dependencies
    rm -rf /tmp && \
    # add new user inside the image, not to use the root user
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# update the Environment
ENV PATH="/py/bin:$PATH"

USER django-user