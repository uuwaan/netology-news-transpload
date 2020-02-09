import os
import requests

IN_DIR = "news"
OUT_DIR = "news_trans"
TRANS_NEWS = ["DE.txt", "FR.txt", "ES.txt"]

ERR_WEIRD_PARAMS = "Непредвиденные параметры в ответе сервера: {0}"

MSG_TRANSLATED = "Файл переведен: {0}"
MSG_UPLOADED = "Файл загружен: {0}"


class YaTranslateAPI:
    API_URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"

    def __init__(self, api_key):
        self._api_key = api_key

    def translate_text(self, txt, from_lang, to_lang="ru"):
        from_lang = from_lang.lower()
        to_lang = to_lang.lower()
        req_params = {
            "key": self._api_key,
            "text": txt,
            "lang": "{0}-{1}".format(from_lang, to_lang),
        }
        resp = requests.get(self.API_URL, params=req_params)
        resp.raise_for_status()
        resp_json = resp.json()
        return "".join(resp_json["text"])


class YaDiskAPI:
    API_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"

    def __init__(self, api_token):
        self._req_headers = {
            "Authorization": "OAuth " + api_token,
        }

    def upload(self, file_path, disk_path, overwrite=True):
        up_link = self._upload_link(disk_path, overwrite)
        with open(file_path, "rb") as up_file:
            resp = requests.put(
                up_link, data=up_file, headers=self._req_headers
            )
            resp.raise_for_status()

    def _upload_link(self, disk_path, overwrite):
        req_params = {
            "path": disk_path,
            "overwrite": bool(overwrite),
        }
        resp = requests.get(
            self.API_URL, params=req_params, headers=self._req_headers
        )
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json["method"] != "PUT" or resp_json["templated"]:
            raise RuntimeError(ERR_WEIRD_PARAMS.format(resp.content))
        return resp_json["href"]


def translate_it(trans_api, in_path, out_path, from_lang, to_lang="ru"):
    news_lang, _ = os.path.splitext(news_file)
    with open(in_path, "r") as in_file:
        out_txt = trans_api.translate_text(in_file.read(), from_lang, to_lang)
    with open(out_path, "w") as out_file:
        out_file.write(out_txt)


if __name__ == "__main__":
    with open("trans_key.txt", "r") as api_file:
        yatran_key = api_file.readline()
    with open("yadisk_token.txt", "r") as api_file:
        yadisk_token = api_file.readline()
    yatran_api = YaTranslateAPI(yatran_key)
    yadisk_api = YaDiskAPI(yadisk_token)
    for news_file in TRANS_NEWS:
        in_path = os.path.join(IN_DIR, news_file)
        out_path = os.path.join(OUT_DIR, news_file)
        news_lang, _ = os.path.splitext(news_file)
        translate_it(yatran_api, in_path, out_path, news_lang)
        print(MSG_TRANSLATED.format(news_file))
        yadisk_api.upload(out_path, news_file)
        print(MSG_UPLOADED.format(news_file))
