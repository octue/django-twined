import logging
import os
import dramatiq
from django.conf import settings
from django_twined.messages import ReelMessage
from octue import Runner


logger = logging.getLogger(__name__)


INPUT_STRANDS = ("input_values", "input_manifest", "credentials", "children")


@dramatiq.actor
def asker(service_name, service_version, analysis_id, input_values=None, input_manifest=None):
    """We probably want to replace all this with GCP Pub/Sub and a set of service accounts"""

    # Acknowledge the start of the run
    ask_group_name = f"analysis-{analysis_id}"
    ReelMessage(action="analysis", status="started", value=analysis_id).group_send(ask_group_name)

    try:
        # Configure the app
        service_configuration = settings.SERVICES[service_name][service_version]
        app_path = service_configuration.pop("app_path")
        twine_file = os.path.join(app_path, "twine.json")
        runner = Runner(
            app_src=app_path,
            twine=twine_file,
            **service_configuration,
        )
        logger.debug(f"Configured Runner for analysis {analysis_id}. Running...")

        # Run the app
        try:
            analysis = runner.run(input_values=input_values, input_manifest=input_manifest)
            logger.debug(f"Completed analysis {analysis_id}. Finalising...")

            results = analysis.finalise(output_dir=os.path.join("data", "output"))
            logger.debug(f"Finalised analysis {analysis_id}")

        except Exception as e:
            # Exception caused by the analysis, not the runner. Return message to the caller.
            ReelMessage(action="ask", status="error", value=analysis_id, hints=e.args[0]).group_send(ask_group_name)
            return

        # Create the completion message
        ReelMessage(action="ask", status="complete", value=analysis_id, **results).group_send(ask_group_name)

    except Exception as e:
        # Exception caused by the analysis, not the runner. Return message to the caller.
        ReelMessage(
            action="ask",
            status="error",
            value=analysis_id,
            hints="Internal error occurred. Could not complete analysis. Your error has been logged for examination.",
        ).group_send(ask_group_name)
        raise e


def ask(analysis_id, message):
    """Start the ask process. Returns a ReelMessage that can be sent to confirm the ask has been queued."""

    # Get only the twine arguments
    kwargs = dict((k, getattr(message, k, None)) for k in INPUT_STRANDS)
    asker.send(analysis_id, **kwargs)

    return ReelMessage(action=message.action, reference=message.reference, status="queued", value=analysis_id)
