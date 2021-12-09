# kube-cron-monitor
Python script for minitoring kubernetes cronjobs and exposing next metris in prometheus format:
* status of all jobs (example: `job_status{cronjob_name="kubernetes-cron-job",job_name="kubernetes-cron-job-1639062000",namespace="default"} 0.0`)
* if any of kube cronjob missed their schedule period (example: `cron_last_schedule_time{cronjob_name="kubernetes-cron-job",namespace="default"} 0.0`)

0 - success

1 - failed

## Huw to run the app

1) First of all set docker image name for the app in:
* **Makefile** - `DOCKER_IMAGE_NAME:=<image_name>` (example: `DOCKER_IMAGE_NAME:=myhub.mydomen.com/kube-cron-monitor`)
* **kube-cron-monitor.yaml** - `image:<image_name>:<image_tag>` (example: `image: myhub.mydomen.com/kube-cron-monitor:1.0.1`)

2) Run `make release` to build and push new image to registry.
3) Run `kubectl apply -f kube-cron-monitor.yaml` to deploy the app to kubernetes

The metrics will be available by url (kube-cron-monitor:8080) inside the cluster.
