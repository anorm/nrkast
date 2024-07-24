FROM python:3.12
WORKDIR /code
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./nrkast /code/nrkast
#COPY ./static /code/static
CMD ["uvicorn", "nrkast.main:app", "--host", "0.0.0.0", "--port", "80"]
