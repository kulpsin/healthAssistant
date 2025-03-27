FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY database.py ./
COPY index_fhir.py ./
COPY patient.py ./
COPY main.py ./


#CMD [ "python", "./main.py" ]
CMD [ "fastapi", "run", "main.py" ]
