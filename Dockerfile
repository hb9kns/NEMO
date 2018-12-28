FROM python:3.6

# Intall NEMO (in the current directory) and Gunicorn
COPY . /nemo/
RUN pip install /nemo/ gunicorn
RUN rm --recursive --force /nemo/

RUN mkdir /nemo
ENV DJANGO_SETTINGS_MODULE "settings"
ENV PYTHONPATH "/nemo/"

EXPOSE 8000/tcp

RUN apt-get update && apt-get install -y dos2unix

COPY start_NEMO_in_Docker.sh /usr/local/bin/
RUN dos2unix /usr/local/bin/start_NEMO_in_Docker.sh && apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*
RUN chmod +x /usr/local/bin/start_NEMO_in_Docker.sh
CMD ["start_NEMO_in_Docker.sh"]
