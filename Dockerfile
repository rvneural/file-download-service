FROM python:3.10.15-bookworm
LABEL maintainer="gafarov@realnoevremya.ru"
RUN apt-get update -y
RUN apt-get install -y ca-certificates
RUN apt-get install -y ffmpeg
EXPOSE 8084
COPY main.py .
COPY requirements.txt .
RUN mkdir downloads
RUN pip install -r requirements.txt
CMD ["python", "main.py"]