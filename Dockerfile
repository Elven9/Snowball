FROM python:3.12.4-bookworm

COPY . /app
WORKDIR /app

# install pipx, poetry
RUN python -m pip install --user pipx && \
    python -m pipx ensurepath && \
    python -m pip install poetry && \
    poetry install

# run the app
CMD ["poetry", "run", "python", "snowball-local/main.py"]
