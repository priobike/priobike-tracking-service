FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install libraries needed for GeoDjango and PostGIS
# See https://docs.djangoproject.com/en/3.2/ref/contrib/gis/install/geolibs/
RUN apt-get update && apt-get install -y \
  binutils \
  libproj-dev \
  gdal-bin

# Install Postgres client to check liveness of the database
RUN apt-get update && apt-get install -y postgresql-client

# Install Poetry as the package manager for this application
RUN pip install poetry

WORKDIR /code

# Use the admin interface to check the health of the application
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/admin || exit 1

# Install Python dependencies separated from the
# run script to enable Docker caching
ADD pyproject.toml /code
RUN poetry install --no-interaction --no-ansi --no-dev

ADD . /code
