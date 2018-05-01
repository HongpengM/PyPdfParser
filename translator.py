import http.client
from hashlib import md5 as md5
import urllib


import random
import json
import re
import warnings
_default_appid_file = 'translator.appid'


class Translator(object):
    """docstring for Translator"""

    def __init__(self, api='baidu', appid=_default_appid_file, toLang='zh'):
        super(Translator, self).__init__()
        if api == 'baidu':
            self.translateMethod = self._translateByBaidu
            self.toLang = toLang
        try:
            self.appid, self.key = Translator.readAppid(file=appid)
        except FileNotFoundError:
            print('No translator appid&key file')

    @classmethod
    def readAppid(cls, file=_default_appid_file):
        appid = {'appid': None, 'key': None}
        with open(file) as f:
            for i in f.readlines():
                for info in appid.keys():
                    if info in i:
                        key = i.split('=')[0].replace('_', '').strip()
                        value = i.split('=')[1].strip()
                        appid[key] = value
        for i in appid.values():
            if not i:
                warnings.warn('Appid not fulfilled')
        return (appid['appid'], appid['key'])

    @classmethod
    def saltedMd5(cls, appid, q, key):
        salt = random.randint(32768, 65536)
        sign = appid + q + str(salt) + key
        m1 = md5()
        m1.update(sign.encode('utf-8'))
        sign = m1.hexdigest()
        return (salt, sign)

    def translate(self, text, fromLang='auto', toLang='zh'):
        def chunkstring(string, length):
            return (string[0 + i:length + i] for i in range(0, len(string), length))
        _ = []
        split_by_paragraph = text.split('.\n')
        _split_paragraph = True
        for i in split_by_paragraph:
            if len(i) > 1900:
                _split_paragraph = False
        if _split_paragraph:
            text = split_by_paragraph
        else:
            text = chunkstring(text, 1500)
        for i in text:
            _.append(self.translateMethod(i, toLang=self.toLang))
        translatedTxt = ''
        for i in _:
            try:
                if _split_paragraph and i:
                    translatedTxt += i + '\n'
                elif i:
                    translatedTxt += i
            except TypeError:
                if len(translatedTxt) < 20:
                    msg = '\n' + translatedTxt
                else:
                    msg = '\n' + translatedTxt[-20:-1]
                raise Warning('Warning: Maybe translated error after:' + msg)

                # print(i)
        return translatedTxt

    def _translateByBaidu(self, text, fromLang='auto', toLang='zh'):
        httpClient = None
        myurl = '/api/trans/vip/translate'
        q = text
        salt, sign = Translator.saltedMd5(self.appid, text, self.key)
        myurl = myurl + '?appid=' + self.appid + '&q=' + \
            urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + \
            toLang + '&salt=' + str(salt) + '&sign=' + sign
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)

            # response是HTTPResponse对象
            response = httpClient.getresponse()
            result = response.read().decode('utf-8')
            data = json.loads(result)
            return data["trans_result"][0]["dst"]
        except Exception as e:
            print(e)
        finally:
            if httpClient:
                httpClient.close()


if __name__ == '__main__':

    txt = 'This is a pig'
    translator = Translator()
    print(translator.translate(txt))
    # print(TranslateByBaidu(txt))
