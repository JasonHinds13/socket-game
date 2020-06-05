from logging import Filter
from flask import has_request_context, request
from re import search, sub


class LogFilter(Filter):

    def filter(self, record):
        if has_request_context():
            record.remote_addr = request.remote_addr
        else:
            ip_pattern = '([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|(\d{1,3}\.){3}\d{1,3}'
            date_pattern = '(\d{2})\/(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\/(\d{4}) (\d{2}):(\d{2}):(\d{2})'
            replace_pattern = ip_pattern+' - - \['+date_pattern+'\]\s'

            ip_search_result = search(ip_pattern, record.msg)
            record.remote_addr = None if ip_search_result is None else ip_search_result.group(0)

            new_message = sub(replace_pattern, '', record.msg)

            record.msg = new_message if new_message != record.msg else record.msg

        return True
