# Contruction of an image

# python with no extras
FROM python:3.14-slim 
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*

# copy configs for installing packages
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src

# install packages
RUN pip install --no-cache-dir -e .

# copy everything else
COPY . .

# use the Makefille
CMD ["make", "all"]