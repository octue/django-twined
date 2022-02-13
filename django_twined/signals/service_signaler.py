import django.dispatch


question_sent = django.dispatch.Signal()

answer_received = django.dispatch.Signal()

monitor_updated = django.dispatch.Signal()

logstream_updated = django.dispatch.Signal()


class ServiceSignaler:
    def send_question_sent(self, question):
        question_sent.send(sender=self.__class__, question=question)

    def send_answer_received(self, answer):
        answer_received.send(sender=self.__class__, answer=answer)

    def send_monitor_updated(self, monitor):
        monitor_updated.send(sender=self.__class__, monitor=monitor)

    def send_logstream_updated(self, logentry):
        logstream_updated.send(sender=self.__class__, logentry=logentry)
