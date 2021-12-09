import prometheus_client as prom
import random
import time
import json
import re
from datetime import datetime
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from croniter import croniter

# Variables
exposed_port = 8080

# The function expose metrics in prometheus format
def expose_metrics():
    gauge_job = prom.Gauge(
        'job_status', \
        'Return job status', \
        ['job_name', 'cronjob_name', 'namespace']
    )
    gauge_cronjob = prom.Gauge(
        'cron_last_schedule_time', \
        'Check if any of kube cronjob missed their schedule period', \
        ['cronjob_name', 'namespace']
    )
    prom.start_http_server(exposed_port)

    while True:
        jobs = jobs_info()
        for job in jobs:
            gauge_job.labels(
                job_name=job['job_name'], \
                cronjob_name=job['cronjob_name'], \
                namespace=job['namespace']
            ).set(job['job_status'])

        cronjobs = cronjobs_info()
        for cronjob in cronjobs:
            gauge_cronjob.labels(
                cronjob_name=cronjob['name'], \
                namespace=cronjob['namespace']
            ).set(cronjob['last_schedule_status'])
        time.sleep(5)

# The function gets all jobs and and check their status
def jobs_info():
    jobs = []
    api_instance = client.BatchV1Api()
    try:
        api_response = api_instance.list_job_for_all_namespaces()
        for item in api_response.items:
            if item.status.active is None:
                if (item.status.succeeded is None and \
                   item.status.failed is not None) or \
                   item.status.conditions[0].type == "Failed":
                    job_status = 1
                else:
                    job_status = 0
                jobs.append({
                    'job_name': item.metadata.name,
                    'cronjob_name': re.sub(r'-\d{10}$', "", item.metadata.name),
                    'namespace': item.metadata.namespace,
                    'job_status': job_status
                })
    except ApiException as e:
        print("Exception when calling BatchV1Api->list_job_for_all_namespaces: %s\n" % e)
    return jobs

# The function gets all cronjobs
def cronjobs_info():
    cronjobs = []
    api_instance = client.BatchV1beta1Api()
    try:
        api_response = api_instance.list_cron_job_for_all_namespaces()
        for item in api_response.items:
            last_schedule_time = item.status.last_schedule_time.timestamp()
            schedule = item.spec.schedule
            last_schedule_status = check_schedule_period(last_schedule_time, schedule)
            cronjobs.append({
                'name': item.metadata.name,
                'namespace': item.metadata.namespace,
                'last_schedule_status': last_schedule_status
            })
    except ApiException as e:
        print("Exception when calling BatchV1beta1Api->list_cron_job_for_all_namespaces: %s\n" % e)
    return cronjobs

# The function checks if any of cronjobs missed their scheduling periods
def check_schedule_period(last_schedule_time, schedule):
    now = datetime.utcnow()
    iter = croniter(schedule, now).get_prev()
    if int(iter) > int(last_schedule_time):
        return 1
    else:
        return 0

if __name__ == '__main__':
    config.load_incluster_config()
    expose_metrics()
