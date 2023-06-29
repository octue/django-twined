from io import StringIO

from django.core.management import call_command


class CallCommandMixin:
    """Mixin providing self.callCommand method to call a management command"""

    @staticmethod
    def callCommand(command, *args, **kwargs):
        """Call a django management command from within a test case
        Handles the iostream so you can test contents of stdout and stderr
        """
        out = StringIO()
        err = StringIO()
        call_command(
            command,
            *args,
            stdout=out,
            stderr=err,
            **kwargs,
        )
        return out, err
