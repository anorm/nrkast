FROM python:3.12-alpine as base

FROM base as requirements
RUN pip install toml-to-requirements
WORKDIR /src
COPY pyproject.toml .
RUN toml-to-req --toml-file pyproject.toml

FROM base as final
WORKDIR /src
COPY --from=requirements /src/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "nrkast.server:app"]
