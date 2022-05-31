from django.dispatch import Signal


question_asked = Signal()

service_usage_event_received = Signal()

answer_received = Signal()

monitor_updated = Signal()

logstream_updated = Signal()


class DjangoTwinedSignals:
    """A signaller class allowing a receiver to listen for all django_twined signals at once by the sender"""

    def send_question_asked(self, question):
        """Send a question_asked signal"""
        question_asked.send(sender=self.__class__, question=question)

    def send_answer_received(self, answer):
        """Send an answer_received signal"""
        answer_received.send(sender=self.__class__, answer=answer)

    def send_monitor_updated(self, monitor):
        """Send a monitor_updated signal"""
        monitor_updated.send(sender=self.__class__, monitor=monitor)

    def send_logstream_updated(self, logentry):
        """Send a logstream_updated signal"""
        logstream_updated.send(sender=self.__class__, logentry=logentry)
