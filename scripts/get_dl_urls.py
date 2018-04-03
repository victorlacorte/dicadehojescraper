import csv
import requests
import sys
from utils.requests_utils import downloadable_urls
from sensitive_info import *


reports = f'{base_url}/carteira-dica-de-hoje-relatorios'
login = f'{base_url}/wp-login.php'
# https://www.iana.org/assignments/media-types/media-types.xhtml
mimes_csv = 'data/mime_types/mimes.csv'
# http://www.useragentstring.com/index.php?id=19830
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)' \
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1' \
        ' Safari/537.36'}
timeout = (5, 10)

if __name__ == '__main__':
    fname = sys.argv[1]
    with requests.Session() as s:
        s.headers.update(headers)
        s.post(login, data=login_payload)
        mimes = set()
        with open(mimes_csv, 'r') as m:
            reader = csv.DictReader(m)
            for row in reader:
                r = row['Template']
                if r:
                    mimes.add(r)
        with open(fname, 'w') as f:
            for ret in downloadable_urls({base_url}, s, domains, mimes,
                    timeout_min=timeout[0], timeout_max=timeout[1]):
                print(ret, file=f)
