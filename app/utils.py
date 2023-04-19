import collections
import logging
import re
import socket

logger = logging.getLogger(__name__)

# IPアドレスを正規表現で指定（先頭3つをprefix_host, 後ろ1つをlast_ip とする）
RE_IP = re.compile('(?P<prefix_host>^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.)(?P<last_ip>\\d{1,3}$)')

def sorted_dict_by_key(unsorted_dict):
    return collections.OrderedDict(sorted(unsorted_dict.items(), key=lambda d:d[0]))

def pprint(chains):
    print(f'\n{">"*40} START {">"*40}')
    for i, chain in enumerate(chains):
        print(f'{"="*25} Chain {i} {"="*25}')
        for k, v in chain.items():
            if k == 'transactions':
                print(k)
                for d in v:
                    print(f'{"-"*40}')
                    for kk, vv in d.items():
                        print(f' {kk:30}{vv}')
            else:
                print(f'{k:15}{v}')

# 他のノードとのソケット接続確認
def is_found_host(target, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((target, port))
            return True
        except Exception as ex:
            logger.error({
                'action': 'is_found_host',
                'target': target,
                'posrt': port,
                'ex': ex
            })
            return False

# 指定したIPアドレスに対する探索範囲を指定してソケット通信できるか確認
def find_neighbours(my_host, my_port, start_ip_range, end_ip_range, start_port, end_port):
    address = f'{my_host}:{my_port}'
    m = RE_IP.search(my_host)
    if not m:
        return None
    prefix_host = m.group('prefix_host')
    last_ip = m.group('last_ip')

    neighbours = []
    logger.info(1111111111111111)
    for guess_port in range(start_port, end_port):
        for ip_range in range(start_ip_range, end_ip_range):
            guess_host = f'{prefix_host}{int(last_ip)+int(ip_range)}'
            guess_address = f'{guess_host}:{guess_port}'
            # 探索範囲のアドレス&ポートに接続できるか（自分自身は除外）
            if is_found_host(guess_host, guess_port) and not guess_address == address:
                neighbours.append(guess_address)
    return neighbours

# 自分自身のIPアドレスを取得
def get_host():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as ex:
        logger.debug({'action': 'get_host', 'ex': ex})
    return '127.0.0.1'

if __name__ == '__main__':
    # print(is_found_host('127.0.0.0', 5001))

    # IPアドレス：192.168.0.10 - 192.168.0.12 かつ ポート：5001 - 5003 まで接続確認
    # print(find_neighbours('192.168.0.10', 5001, 0, 3, 5001, 5003))

    # print(is_found_host('127.0.0.0', 5001))
    # print(is_found_host('127.0.0.0', 5002))
    # print(is_found_host('127.0.0.0', 5003))
    # print(is_found_host('127.0.1.2', 5001))
    # print(find_neighbours('127.0.0.0', 5001, 0, 3, 5001, 5010))
    print(get_host())
