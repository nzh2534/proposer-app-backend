FROM python:3.9.16-slim-buster as builder

COPY requirements.txt /app/requirements.txt

RUN apt-get update \
  && apt-get -y install --upgrade git \
  && apt-get -y install --no-install-recommends libpq-dev gcc g++ libgl1 \
  && apt-get -y install tesseract-ocr tesseract-ocr-eng

RUN set -ex \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install layoutparser \
    && pip install https://download.pytorch.org/whl/cpu/torch-2.0.0%2Bcpu-cp39-cp39-linux_x86_64.whl \
    && pip install https://download.pytorch.org/whl/cpu/torchvision-0.15.0%2Bcpu-cp39-cp39-linux_x86_64.whl \
    && pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git@v0.5#egg=detectron2"


WORKDIR /app
ADD . .

# ENV PYTHONPATH "${PYTHONPATH}:/app/"

CMD gunicorn fhphome.wsgi:application --timeout 5000 --bind 0.0.0.0:$PORT

# EXPOSE 8000

# CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "--timeout", "5000", "fhphome.wsgi:application"]