FROM python:3.7-slim
MAINTAINER yury.goncharuk@gmail.com

COPY rootfs/ /

RUN pip3 install -r /opt/kube_cron_monitor/requirements.txt

ENTRYPOINT python3 /opt/kube_cron_monitor/kube_cron_monitor.py
