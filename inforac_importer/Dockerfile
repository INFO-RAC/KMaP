FROM python:3.10.13-slim-bookworm
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt install cron vim systemd -y

COPY inforac_importer/ /usr/src/inforac_importer/
RUN pip3 install -r /usr/src/inforac_importer/requirements.txt
RUN echo "alias ll='ls -al'" >> ~/.bashrc

CMD ["bash"]