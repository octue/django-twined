from django.dispatch import Signal


delivery_acknowledgement_received = Signal()
exception_received = Signal()
heartbeat_received = Signal()
log_record_received = Signal()
monitor_message_received = Signal()
question_asked = Signal()
result_received = Signal()
