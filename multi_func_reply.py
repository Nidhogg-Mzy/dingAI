import base64
import json
import os
import requests
from binascii import hexlify
from Crypto.Cipher import AES


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.77 Safari/537.36',
}


class Encrypted:

    def __init__(self):
        self.pub_key = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e41' \
                       '7629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575c' \
                       'ce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7 '
        self.nonce = '0CoJUm6Qyw8W8jud'

    @staticmethod
    def create_secret_key(size):
        return hexlify(os.urandom(size))[:16].decode('utf-8')

    @staticmethod
    def aes_encrypt(text, key):
        iv = '0102030405060708'
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        result = encryptor.encrypt(text.encode("utf-8"))
        result_str = base64.b64encode(result).decode('utf-8')
        return result_str

    @staticmethod
    def rsa_encrypt(text, pub_key, modulus):
        text = text[::-1]
        rs = pow(int(hexlify(text.encode('utf-8')), 16), int(pub_key, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)

    def work(self, ids, br=128000):
        text = {'ids': [ids], 'br': br, 'csrf_token': ''}
        text = json.dumps(text)
        i = self.create_secret_key(16)
        enc_text = self.aes_encrypt(text, self.nonce)
        enc_text = self.aes_encrypt(enc_text, i)
        enc_sec_key = self.rsa_encrypt(i, self.pub_key, self.modulus)
        data = {'params': enc_text, 'encSecKey': enc_sec_key}
        return data

    def search(self, text):
        text = json.dumps(text)
        i = self.create_secret_key(16)
        enc_text = self.aes_encrypt(text, self.nonce)
        enc_text = self.aes_encrypt(enc_text, i)
        enc_sec_key = self.rsa_encrypt(i, self.pub_key, self.modulus)
        data = {'params': enc_text, 'encSecKey': enc_sec_key}
        return data


class Search:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.'
                          '2883.87 Safari/537.36',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/'}
        self.main_url = 'http://music.163.com/'
        self.session = requests.Session()
        self.session.headers = self.headers
        self.ep = Encrypted()

    def search_song(self, search_content, search_type=1, limit=10):
        song_id_list = []
        url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        text = {'s': search_content, 'type': search_type, 'offset': 0, 'sub': 'false', 'limit': limit}
        data = self.ep.search(text)
        resp = self.session.post(url, data=data)
        result = resp.json()
        if result['result']['songCount'] <= 0:
            return None
        else:
            songs = result['result']['songs']
            for song in songs:
                song_id, song_name, singer, alia = song['id'], song['name'], song['ar'][0]['name'], song['al']['name']
                song_id_list.append(song_id)
        return song_id_list[0]


def get_lyrics_pro(id):
    link = 'http://music.163.com/api/song/media?id=' + str(id)
    web_data = requests.get(url=link, headers=headers).text
    json_data = json.loads(web_data)
    try:
        return json_data['lyric']
    except BaseException:
        return "出错啦，换首别的试试吧！！！"
