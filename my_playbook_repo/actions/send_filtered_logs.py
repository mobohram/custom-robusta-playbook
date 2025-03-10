from robusta.api import action, PrometheusKubernetesAlert, MarkdownBlock, FileBlock
from my_playbook_repo.params.log_filter_params import LogFilterParams
import logging

@action
def send_filtered_logs(alert: PrometheusKubernetesAlert, params: LogFilterParams):
    pod = alert.get_pod()
    if not pod:
        logging.error(f"No pod found for alert: {alert.alert_name}")
        return

    logs = pod.get_logs()
    filtered_logs = "\n".join(
        line for line in logs.splitlines() if any(keyword in line for keyword in params.keywords)
    )

    if not filtered_logs:
        filtered_logs = f"No entries containing {params.keywords} found in the logs."

    alert.add_enrichment(
        [
            MarkdownBlock(f"**Filtered logs for pod {pod.metadata.name}:**"),
            FileBlock(f"{pod.metadata.name}_filtered_logs.log", filtered_logs),
        ]
    )
