#!/usr/bin/env python3
import os
import json
import gzip
import re
import datetime
import urllib.parse
from json.decoder import JSONDecodeError
from url_patterns import urlpatterns

course_regex = re.compile(r'course-v1:([\w_\-]+)\+([\w_\-]+)\+([\w_\-]+)')
block_regex = re.compile(r'block-v1:([\w_\-]+)\+([\w_\-]+)\+([\w_\-]+)+\+type@([\w_\-]+)\+block@[\w_\-]+')
valid_key = re.compile(r'^[a-zA-Z0-9_\-.]+$')
code_in_key = re.compile(r'[a-z0-9]{32}')


def make_json(value, prefix):
    """
    Returns always a dict.
    If value is a dict, returns it unchanged.
    If it is a string representing a json, returns the json converted to dict
    If it is a plain string, returns { <prefix>_str: <value> }
    If it is a list, returns { <prefix>_list: <value> }
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        return {prefix + '_list': value}
    try:
        return json.loads(value)
    except ValueError:
        return {prefix + '_str': value}


def course_from_string(string):
    m = course_regex.search(str(string))

    if m:
        return {'id': m.group(0),
                'org': m.group(1),
                'code': m.group(2),
                'run': m.group(3)}
    else:
        return None


def block_from_string(string):

    m = block_regex.search(urllib.parse.unquote(str(string)))

    if m:
        return {'id': m.group(0),
                'org': m.group(1),
                'code': m.group(2),
                'run': m.group(3),
                'type': m.group(4)}
    else:
        return None


def fix_keys(dict_arg):
    """
    If the key has invalid characters or looks like a 32-byte code, it is converted to struct in the form
    { 'key': <orignal key>,
      'value': <value of the original key>
    }
    If the value is a dict, applies the function recursively
    :param dict_arg: a dict
    :return: None
    """
    keys = list(dict_arg.keys())
    new_keys = []
    for key in keys:
        # Calls itself recurrently if it contains a dict
        if isinstance(dict_arg[key], dict) and dict_arg[key]:
            fix_keys(dict_arg[key])

        # Detects keys with json or code values and converts it to value
        if not valid_key.match(key) or code_in_key.search(key):
            new_keys.append({'key': make_json(key, 'key'),
                             'value': dict_arg[key]
                             })
            del dict_arg[key]

    if new_keys:
        dict_arg['keys'] = new_keys


def fix_row(row, filename):
    try:
        j = json.loads(row)
    except JSONDecodeError as e:
        # In some very long events, the row is truncated at 32768 chars, leading to an invalid json
        j = {
            'event_key': 'error',
            'event_type': 'error',
            'event': {'error': str(e),
                      'original log': str(row)},
            'course': course_from_string(row),
            'filename': filename
        }
        return json.dumps(j), None

    if len(j['event_type']) > 0 and j['event_type'][0] == '/':
        event_key = j['event_type'][1:]
        j['event_key'] = 'unknown_url'
        for urlpattern in urlpatterns:
            match = re.match(urlpattern[0], event_key)
            if match:
                j['event_key'] = 'url:{}'.format(urlpattern[1])
                break
    else:
        j['event_key'] = j['event_type']

    # Extracts the course id from the event
    course = course_from_string(j['event_type'])
    if not course:
        course = course_from_string(j['event'])
    if course:
        j['course'] = course

    # Extracts the block from the event id where available
    block = block_from_string(j['event_type'])
    if not block and 'referer' in j:
        block = block_from_string(j['referer'])
    if not block:
        block = block_from_string(j['event'])
    if block:
        j['block_id'] = block['id']
        if not course:
            j['course'] = {'id': 'course-v1:' + block['org'] + '+' + block['code'] + '+' + block['run'],
                           'org': block['org'],
                           'code': block['code'],
                           'run': block['run']}

    j['filename'] = filename

    # Extracts the timestamp
    timestamp = datetime.datetime.fromisoformat(j['time'])
    row_date = datetime.datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day)

    return json.dumps(j), row_date


def fix_file(filename, dest_base_path, lms):
    source = gzip.open(filename)
    try:
        current_date = None
        file_counter = 1
        dest = None
        keys = []

        try:
            for row in source:
                new_row, new_date = fix_row(row, filename)
                # If the row had invalid json, new_date is None. If the dest file existed, it is possible to log the
                # output assuming the same date as the previous event. If the dest file does not exist it means that
                # it is the first row in the file. We just discard it
                if not new_date:
                    if dest:
                        new_date = current_date
                    else:
                        continue

                # If a new date is detected, or it is the first row in the file, open the destination file
                if new_date != current_date:

                    # To allow partitioning in S3, the destination path is made of lms and date
                    dest_rel_path = os.path.join(
                        'lms={}'.format(lms),
                        'year={0:04d}'.format(new_date.year),
                        'month={0:02d}'.format(new_date.month),
                        'day={0:02d}'.format(new_date.day)
                    )
                    dest_path = os.path.join(dest_base_path, dest_rel_path)
                    os.makedirs(dest_path, exist_ok=True)

                    # In case a log file contains more than one date, appends a incremental counter to the filename
                    dest_filename = '{}_{}.gz'.format(os.path.basename(filename)[:-3], file_counter)

                    # Returns a list of filename with relative path, useful for uploading to s3
                    keys.append(os.path.join(dest_rel_path, dest_filename))

                    # If it is a new file, the destination will not exist. Otherwise we need to close the previous one
                    # before creating the new one
                    if dest:
                        dest.close()
                    dest = gzip.open(os.path.join(dest_path, dest_filename), 'wb')

                    current_date = new_date
                    file_counter += 1

                dest.write(new_row.encode('utf-8') + '\r\n'.encode('utf-8'))
        finally:
            if dest:
                dest.close()
    finally:
        source.close()

    return keys
