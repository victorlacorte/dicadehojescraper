import requests
import sys
from utils.requests_utils import downloadable_urls
from sensitive_info import *

reports = f'{base_url}/carteira-dica-de-hoje-relatorios'
login = f'{base_url}/wp-login.php'

if __name__ == '__main__':
    fname = sys.argv[1]
    with requests.Session() as s:
        s.post(login, data=login_payload)
        with open(fname, 'w') as f:
            for url in downloadable_urls({base_url}, s, domains):
                print(url, file=f)
