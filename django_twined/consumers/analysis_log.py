import logging
from channels.generic.websocket import WebsocketConsumer
from django_twined.messages import ReelMessage


logger = logging.getLogger(__name__)


class AnalysisLogConsumer(WebsocketConsumer):
    """A consumer allowing logs for an analysis to be streamed in plain text directly from a python logger, then
    converted into ReelMessages which get logged to the analysis group.
    """

    @property
    def analysis_id(self):
        return str(self.scope["url_route"]["kwargs"].get("analysis_id"))

    @property
    def analysis_group_name(self):
        return f"analysis-{self.analysis_id}"

    def connect(self):
        """Accept connection to to enable log forwarding to the analysis group"""
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        """Receive log text, wrap it properly as part of the messaging system and forward it to the analysis group"""
        ReelMessage(action="log", value=text_data).group_send(self.analysis_group_name)
