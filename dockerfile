FROM python:3.9-slim

WORKDIR /edu_pad

COPY . .

RUN mkdir -p static/csv static/db

RUN pip install --upgrade pip \
    && pip install -e . \
    && rm -rf /root/.cache/pip

ENV PYTHONPATH=/edu_pad/src


ENTRYPOINT ["python", "-m"]


CMD ["edu_pad.main_extractor"]

