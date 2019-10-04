FROM mariadb:10 as maria
FROM python:3.7

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY --from=maria /usr/bin/mysqldump /usr/bin/mysqldump

COPY . .

CMD [ "python", "-u", "/app/main.py" ]
