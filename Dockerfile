FROM python:3.12
WORKDIR /code
COPY . .
RUN pip install .
COPY ./nrkast /code/nrkast
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "nrkast.server:app"]
