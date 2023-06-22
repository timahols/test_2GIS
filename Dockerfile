FROM ubuntu:latest
MAINTAINER Tima_holl
# многострочная команда RUN, которая обновляет системный пакет и устанавливает необходимые зависимости для выполнения Selenium-скрипта
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip curl unzip && \
    curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb && \
    apt install -y ./chrome.deb && \
    rm ./chrome.deb && \
    wget https://chromedriver.storage.googleapis.com/92.0.4515.107/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip
# копирует файл requirements.txt из локальной машины в корневую директорию внутри контейнера.
COPY requirements.txt /
# устанавливает Python-библиотеки, указанные в requirements.txt.
RUN pip3 install -r /requirements.txt
# копирует все файлы из текущей локальной директории и загружает их в контейнер.
COPY . /
# устанавливает команду, которую контейнер будет выполнять при запуске, в данном случае это скрипт 2gis.py, написанный на языке Python 3.
CMD ["python3", "2gis.py"]
