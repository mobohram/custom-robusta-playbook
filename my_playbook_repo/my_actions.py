from robusta.api import *
from robusta.core import *
import logging
from typing import List

class LogFilterParams(ActionParams):
    keywords: List[str]


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
    
    labels = alert.alert.labels
    
    desired_labels = {"app", "pod", "type"}
    
    filtered_labels = {key: value for key, value in labels.items() if key in desired_labels}
    
    alert.add_enrichment(
        [
            TableBlock(
                [[k, v] for (k, v) in filtered_labels.items()],
                ["label", "value"],
                table_format=TableBlockFormat.vertical,
                table_name="*Alert labels*",
            ),
        ],
        annotations={SlackAnnotations.ATTACHMENT: True},
        enrichment_type=EnrichmentType.alert_labels,
        title="Alert labels",
    )
