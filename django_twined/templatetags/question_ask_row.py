from django.contrib.admin.templatetags.admin_modify import InclusionAdminNode, register, submit_row


@register.tag(name="question_ask_row")
def question_ask_row_tag(parser, token):
    """Override a the question change form row tag
    https://github.com/django/django/blob/a1e4e86f923dc8387b0a9c3025bdd5d096a6ebb8/django/contrib/admin/templatetags/admin_modify.py#L115
    """
    return InclusionAdminNode(parser, token, func=submit_row, template_name="question_ask_row.html")
