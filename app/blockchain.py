# パッケージ群
import contextlib
import hashlib
import json
import logging
import sys
import time
import threading

# サードパーティ群
from ecdsa import NIST256p
from ecdsa import VerifyingKey

import requests

# 内部ロジック
import utils

MINING_DIFFICULTY = 3
MINING_SENDER = 'THE BLOCKCHAIN'
MINING_REWARD = 1.0
MINING_TIMER_SEC = 20

# 他ノード情報
BLOCKCHAIN_PORT_RANGE = (5001, 5004)
NEIGHBOURS_IP_RANGE_NUM = (0, 1)
BLOCKCHAIN_NEIGHBOURS_SYNC_TIME_SEC = 20

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# ブロックの生成プログラム
#   ・仮想通貨の取引（トランザクション）を保存する
#   ・マイニングによって、
#     ・マイニング報酬用の取引（トランザクション）を保存する
#     ・正しいナンスの取得する
#     ・ナンスと最新のブロック（チェーン先のブロック）のハッシュ値を使ってブロックを生成する
class BlockChain(object):
    def __init__(self, blockchain_address=None, port=None):
        self.transaction_pool = []
        self.chain = []
        self.neighbours = []
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address
        self.port = port
        # 並列処理のプロセス数
        self.mining_semaphore = threading.Semaphore(1)
        self.sync_neighbours_semaphore = threading.Semaphore(1)

    def set_naighbours(self):
        self.neighbours = utils.find_neighbours(
            utils.get_host(), self.port, NEIGHBOURS_IP_RANGE_NUM[0], NEIGHBOURS_IP_RANGE_NUM[1], BLOCKCHAIN_PORT_RANGE[0], BLOCKCHAIN_PORT_RANGE[1]
        )
        logger.info({'action': 'set_neighbours', 'neighbours': self.neighbours})

    def sync_neighbours(self):
        is_acquire = self.sync_neighbours_semaphore.acquire(blocking=False)
        if is_acquire:
            with contextlib.ExitStack() as stack:
                stack.callback(self.sync_neighbours_semaphore.release)
                self.set_naighbours()
                loop = threading.Timer(BLOCKCHAIN_NEIGHBOURS_SYNC_TIME_SEC, self.sync_neighbours)
                loop.start()

    #ブロックの追加
    def create_block(self, nonce, previous_hash):
        block = utils.sorted_dict_by_key({
            'timestamp': time.time(),
            'transactions': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        self.chain.append(block)
        self.transaction_pool = []

        for node in self.neighbours:
            requests.delete(f'http://{node}/transactions')
        return block

    # ハッシュ計算
    def hash(self, block):
        sorted_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(sorted_block.encode()).hexdigest()

    # トランザクションプールからブロックを追加
    def add_transaction(
        self,
        sender_blockchain_address,
        recipient_blockchain_address,
        value,
        sender_public_key=None,
        signature=None
    ):
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_blockchain_address,
            'recipient_blockchain_address': recipient_blockchain_address,
            'value': float(value)
        })
        if sender_blockchain_address == MINING_SENDER:
            self.transaction_pool.append(transaction)
            return True
        if self.verify_transaction_signature(sender_public_key, signature, transaction):
            # if self.calculate_total_amount(sender_blockchain_address) < float(value):
            #     logger.error({'action': 'add_transaction', 'error': 'no_value'})
            #     return False
            self.transaction_pool.append(transaction)
            return True
        return False

    # トランザクションプールからブロックを追加
    def create_transaction(
        self,
        sender_blockchain_address,
        recipient_blockchain_address,
        value,
        sender_public_key,
        signature
    ):
        is_transacted = self.add_transaction(
            sender_blockchain_address,
            recipient_blockchain_address,
            value,
            sender_public_key,
            signature
        )
        # 他ノードへ同期
        if is_transacted:
            for node in self.neighbours:
                requests.put(
                    f'http://{node}/transactions',
                    json={
                        'sender_blockchain_address': sender_blockchain_address,
                        'recipient_blockchain_address': recipient_blockchain_address,
                        'value': value,
                        'sender_public_key': sender_public_key,
                        'signature': signature,
                    }
                )
        return is_transacted

    def verify_transaction_signature(
        self,
        sender_public_key,
        signature,
        transaction
    ):
        sha256 = hashlib.sha256()
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()
        signature_bytes = bytes().fromhex(signature)
        verifying_key = VerifyingKey.from_string(
            bytes().fromhex(sender_public_key), curve=NIST256p
        )
        verified_key = verifying_key.verify(signature_bytes, message)
        return verified_key


    # ナンスの判定（ハッシュ値の先頭が'000'となれば正解とする）
    def valid_proof(self, transactions, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
        guess_block = utils.sorted_dict_by_key({
            'transactions': transactions,
            'previous_hash': previous_hash,
            'nonce': nonce
        })
        guess_hash = self.hash(guess_block)
        return guess_hash[:difficulty] == '0' * difficulty

    # ナンスの生成
    def proof_of_work(self):
        # 生成ブロックするトランザクション
        transactions = self.transaction_pool.copy()
        # 最後に生成したブロックのハッシュ値
        previous_hash = self.hash(self.chain[-1])
        # 正しいナンスの取得
        nonce = 0
        while self.valid_proof(transactions, previous_hash, nonce) is False:
            nonce += 1
        return nonce

    # マイニング
    def mining(self):
        nonce = self.proof_of_work()
        self.add_transaction(
            sender_blockchain_address=MINING_SENDER,
            recipient_blockchain_address=self.blockchain_address,
            value=MINING_REWARD
        )
        previous_hash = self.hash(self.chain[-1])
        self.create_block(nonce, previous_hash)
        logger.info({'action': 'mining', 'status': 'success'})
        return True

    # 仮想通貨の合計値を取得
    def calculate_total_amount(self, blockchain_address):
        total_amount = 0.0
        for block in self.chain:
            for transaction in block['transactions']:
                value = float(transaction['value'])
                if blockchain_address == transaction['recipient_blockchain_address']:
                    total_amount += value
                if blockchain_address == transaction['sender_blockchain_address']:
                    total_amount -= value
        return total_amount

    # 20sec毎にマイニング開始
    def start_mining(self):
        is_acquire = self.mining_semaphore.acquire(blocking=False)
        if is_acquire:
            with contextlib.ExitStack() as stack:
                stack.callback(self.mining_semaphore.release)
                self.mining()
                loop = threading.Timer(MINING_TIMER_SEC, self.start_mining)
                loop.start()

# if __name__ == '__main__':
#     my_blockchain_address = 'my_blockchain_address'

#     block_chain = BlockChain(my_blockchain_address)
#     utils.pprint(block_chain.chain)

#     # ブロック生成前のトランザクションプールに追加
#     block_chain.add_transaction('A', 'B', 1.0)
#     # マイニング（ブロックの生成）
#     block_chain.mining()
#     utils.pprint(block_chain.chain)

#     block_chain.add_transaction('C', 'D', 2.0)
#     block_chain.add_transaction('X', 'Y', 3.0)
#     block_chain.mining()
#     utils.pprint(block_chain.chain)

#     print('my', block_chain.calculate_total_amount(my_blockchain_address))
#     print('C', block_chain.calculate_total_amount('C'))
#     print('D', block_chain.calculate_total_amount('D'))
