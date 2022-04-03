import re


def is_group_name(group_name):
    return re.match('[A-Z]', group_name)
