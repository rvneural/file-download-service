FROM python:3.10.15-bookworm
LABEL maintainer="gafarov@realnoevremya.ru"
RUN apt-get install -y ca-certificates
EXPOSE 8084
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]