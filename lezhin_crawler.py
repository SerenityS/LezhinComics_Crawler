import json
import os
import urllib.request
import re
import requests
import shutil
import zipfile

from bs4 import BeautifulSoup
from sys import stdout
from tqdm import tqdm

# Initial URL & Path
comic_url = "https://www.lezhin.com/ko/comic/"
comic_img_url = "https://cdn.lezhin.com/v2/comics/%s/episodes/%s/contents/scrolls/%s.webp?access_token=%s"
episode_info_url = "http://cdn.lezhin.com/episodes/%s/%s.json?access_token=%s"
login_url = "https://www.lezhin.com/ko/login/submit"

tmp = os.getcwd() + "/tmp"


def get_comics(c_id, e_id, c_num, e_num, token, title):
    # 에피소드 정보(컷수)
    html = urllib.request.urlopen(episode_info_url % (c_id, e_id, token))
    data = json.load(html)

    cut = data["cut"]

    try:
        for i in tqdm(range(1, cut + 1), desc="%s화 " % e_id):
            # 임시 폴더 생성
            if not os.path.isdir(tmp):
                os.mkdir(tmp)

            # 이미지 다운로드
            urllib.request.urlretrieve((comic_img_url % (c_num[0], e_num, str(i), token)),
                                        tmp + ("/%d.webp" % i))
        zip_comics(e_id, title)
        tqdm.write("- %d화 다운로드 성공." % e_id)
    except:
        # 다운로드 실패 - 403 Forbidden
        tqdm.write("- %d화 다운로드에 실패하였습니다. 해당 화 결재 여부를 확인하세요." % e_id)


def get_comics_data(c_id, sess, token):
    html = BeautifulSoup(sess.get(comic_url + c_id).text, "lxml")

    # 만화 제목
    try:
        title = html.find_all(class_="comicInfo__title")[0].text
    except:
        print("\n잘못된 만화 ID입니다. - %s" % c_id)
        exit()

    data = html.find_all("script")

    # 만화의 고유 번호
    c_num = re.findall("parent_id: '([\w0-9]*)'", str(data))

    # 각 에피소드의 고유 번호
    e_nums = re.findall('all: \[([\w\0-힣]*)}],', str(data))
    e_nums = re.findall('"id":([\w0-9]*)', str(e_nums))
    e_nums.reverse()  # n..1 -> 1..n

    # 0화가 있는가?..
    zero = 0
    try:
        urllib.request.urlopen(episode_info_url % (c_id, "0", token))
    except:
        zero = 1
        pass

    return [title, c_num, e_nums, zero]


def get_token(c_id, id, pw, sess):
    # Login to Lezhin
    stdout.write('\r\n레진코믹스 로그인 중입니다...')
    sess.post(login_url, data={'username': id, 'password': pw})

    # Get Access Token
    try:
        token_html = sess.get(comic_url + c_id).text

        html = BeautifulSoup(token_html, "lxml")
        data = html.find_all("script")

        token = re.findall("token: '([\w\--z]*)'", str(data))[0]
        stdout.write('\r레진코믹스 로그인에 성공하였습니다.\n')
        stdout.flush()
        return token
    except IndexError:
        stdout.write('\r레진코믹스 로그인에 실패하였습니다. ID/PW를 다시 확인해주세요.')
        exit()


def zip_comics(e_id, title):
    dir = os.getcwd() + "/" + title

    # 만화 제목으로 폴더 생성
    if not os.path.isdir(dir):
        os.mkdir(dir)

    # 압축 파일 생성
    comic_zip = zipfile.ZipFile(os.getcwd() + ('/%s/%d화.zip' % (title, e_id)), 'w')

    for folder, _, files in os.walk(os.getcwd() + '/tmp'):
        for file in files:
            if file.endswith('.webp'):
                comic_zip.write(os.path.join(folder, file), file, compress_type=zipfile.ZIP_DEFLATED)
    comic_zip.close()

    # 임시 폴더 삭제
    shutil.rmtree(tmp)


if __name__ == "__main__":
    # 시작시 임시 폴더 삭제
    if os.path.isdir(tmp):
        shutil.rmtree(tmp)

    print("레진코믹스 다운로더")

    id = input("\nLezhin ID : ")
    pw = input("Lezhin PW : ")
    c_id = input("Comic_ID : ")  # 만화 고유 ID

    # 완전판 로그인을 위한 로그인 세션 생성
    sess = requests.Session()
    sess.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }

    # 토큰 가져오기
    access_token = get_token(c_id, id, pw, sess)
    
    # 만화 데이터 가져오기
    c_data = get_comics_data(c_id, sess, access_token)

    print("\n작품명 : %s / 총 화수 : %d\n다운로드를 시작합니다.\n" % (c_data[0], len(c_data[2])))

    # 만화 다운로드
    for i in range(0, len(c_data[2])):
        get_comics(c_id, i + c_data[3], c_data[1], c_data[2][i], access_token, c_data[0])
    print("\n다운로드 완료.")