# blockchain-python

## パッケージのインストール
requirements.txtにインストールしたいパッケージを記述し、以下のコマンドでインストールする
```
pip3 install -r requirements.txt
```

## pythonの実行
```
python [ファイル名]
```

### ブロックチェーンノードの起動
```
# デフォルトポート（5001）で起動
python python blockchain_server.py

# 指定ポート（5002）で起動
python python blockchain_server.py -p 5002
```

### ウォレットの起動
```
# デフォルトポート（8080）で起動 & 接続ノードがデフォルト（http://127.0.0.1:5001）
python python wallet_server.py

# 指定ポート（8081）で起動 & 接続ノードを指定（http://127.0.0.1:5002）
python python wallet_server.py -p 8081 -g http://127.0.0.1:5002
```

## ビットコインのブロックチェーンアドレスの生成手順
1. Creating a public key with ECDSA
2. SHA-256 for the public key
3. Ripemd160 for the SHA-256
4. Add network byte
5. Double SHA-256
6. Get checksum
7. Concatenate public key and checksum
8. Encoding the key with Base58

## Flaskについて
https://msiz07-flask-docs-ja.readthedocs.io/ja/latest/
