import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import whois
from dateutil.relativedelta import relativedelta


def main():
    date_to_check = datetime.today() - relativedelta(months=1)
    file_path = get_file_path_from_arguments()

    urls4check = load_urls4check(path=file_path)

    for url in urls4check:
        assert is_server_respond_with_200(url=url), \
            'Server response is not 200.'
        domain_name = get_domain_name_from_url(url=url)
        assert get_domain_expiration_date(domain_name) > date_to_check, \
            'Domain expiration date is less than a month.'
        print('Health of domain {} is Ok!'.format(domain_name))


def load_urls4check(path: str):
    file_data = load_file_data(file_path=path)
    if file_data is None:
        exit('File was not found')
    url_regexp_row = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]| ! ' \
                     '*  \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_regexp_row, file_data)
    if not urls:
        print('There is no urls in file.'
              'Url format: http(s)://example.com')
        return None
    for url in urls:

        yield url


def is_server_respond_with_200(url: str):
    response = requests.get(url=url)

    return response.ok


def get_domain_name_from_url(url: str):
    parsed_uri = urlparse(url=url)
    domain_name = parsed_uri.netloc

    return domain_name


def get_domain_expiration_date(domain_name: str):
    domain = whois.query(domain_name)
    domain_expiration_date = domain.expiration_date

    return domain_expiration_date


def load_file_data(file_path: str):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None


def get_file_path_from_arguments():
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        return None

    assert check_path_is_not_directory(path=path), \
        'Path is a directory, please, try again with file path'

    return path


def check_path_is_not_directory(path: str):
    path_to_check = Path(path)
    return not path_to_check.is_dir()


if __name__ == '__main__':
    main()
