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

    file_data = load_file_data(file_path=file_path)
    if file_data is None:
        print('File was not found')
        return None

    urls4check = load_urls4check(file_data=file_data)
    loop_usage_marker = False
    for url in urls4check:
        loop_usage_marker = True
        domain_name = get_domain_name_from_url(url=url)
        main_page_url = get_main_page_url(url=url)

        domain_response_ok = is_server_respond_with_ok(url=main_page_url)
        domain_expiration_date = get_domain_expiration_date(domain_name)

        if not domain_response_ok:
            print_response_not_ok_error(domain_name=domain_name)

        elif domain_expiration_date <= date_to_check:
            print_expiration_date_error(domain_name)

        elif domain_response_ok and (domain_expiration_date > date_to_check):
            print_domain_health_ok_message(domain_name)

        print('-----------------')

    if not loop_usage_marker:
        print('There is no urls in file.'
              'Url format: http(s)://example.com')


def print_response_not_ok_error(domain_name: str):
    print('Server response for domain {} is not Ok.'.format(domain_name))


def print_expiration_date_error(domain_name: str):
    print('Domain expiration date for domain {} '
          'is less than a month.'.format(domain_name))


def print_domain_health_ok_message(domain_name: str):
    print('Health of domain {} is Ok!'.format(domain_name))


def load_urls4check(file_data: str):
    url_regexp_row = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]| ! ' \
                     '*  \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_regexp_row, file_data)
    for url in urls:
        yield url


def is_server_respond_with_ok(url: str):
    response = requests.get(url=url)

    return response.ok


def get_domain_name_from_url(url: str):
    parsed_uri = urlparse(url=url)
    domain_name = parsed_uri.netloc

    return domain_name


def get_domain_scheme_from_url(url: str):
    parsed_uri = urlparse(url=url)
    domain_name = parsed_uri.scheme

    return domain_name


def get_main_page_url(url: str):
    domain_name = get_domain_name_from_url(url=url)
    domain_scheme = get_domain_scheme_from_url(url=url)

    main_page_url = '{}://{}'.format(domain_scheme,
                                     domain_name)

    return main_page_url


def get_domain_expiration_date(domain_name: str):
    domain = whois.whois(domain_name)
    try:
        domain_expiration_date = domain.expiration_date[0]
    except TypeError:
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
