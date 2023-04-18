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