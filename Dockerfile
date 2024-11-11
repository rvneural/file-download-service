FROM python:3.10.15-bookworm
LABEL maintainer="gafarov@realnoevremya.ru"
EXPOSE 80
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]