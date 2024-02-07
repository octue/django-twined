question_basic_fieldset = (
    None,
    {
        "fields": (
            "id",
            "status",
            "service_revision",
            "asked",
            "answered",
            "latest_heartbeat",
            "duration",
        )
    },
)

question_db_input_values_fieldset = ("Input Values", {"classes": ("collapse",), "fields": ("input_values",)})
question_db_output_values_fieldset = ("Output Values", {"classes": ("collapse",), "fields": ("output_values",)})

question_delivery_ack_fieldset = (
    "Delivery Acknowledgement",
    {"classes": ("collapse",), "fields": ("delivery_acknowledgement",)},
)
question_log_records_fieldset = ("Log Records", {"classes": ("collapse",), "fields": ("log_records",)})
question_monitor_messages_fieldset = ("Monitor Messages", {"classes": ("collapse",), "fields": ("monitor_messages",)})
question_result_fieldset = ("Result", {"classes": ("collapse",), "fields": ("result",)})
question_exceptions_fieldset = ("Exceptions", {"classes": ("collapse",), "fields": ("exceptions",)})
