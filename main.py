# -*- coding: utf-8 -*-

#run on 21:30 every Sunday.
import urllib.request, urllib.error, urllib.parse
import os, sys, re
import subprocess
import base64
import requests
import bs4
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime as dt
import datetime

# common key
auth_key = "bcd151073c03b352e1ef2fd66c32209da9ca0afa"
key_offset = 0

def req_res(url, headers):
    """ do req. and get res.
    """
    req = urllib.request.Request(url, None, headers)
    res = urllib.request.urlopen(req)
    return req, res

def auth1():
    """ get 1st auth
    """
    url = "https://radiko.jp/v2/api/auth1"
    headers, auth_response = {}, {}
    headers = {
                        "User-Agent": "curl/7.56.1",
                        "Accept": "*/*",
                        "X-Radiko-App":"pc_html5",
                        "X-Radiko-App-Version":"0.0.1",
                        "X-Radiko-User":"dummy_user",
                        "X-Radiko-Device":"pc",
                    }
    req, res = req_res(url, headers)
    auth_response["body"], auth_response["headers"] = res.read(), res.info()
    return auth_response

def get_partial_key(auth_response):
    """ get a key and an authtoken
    """
    authtoken = auth_response["headers"]["x-radiko-authtoken"]
    offset, length   = int(auth_response["headers"]["x-radiko-keyoffset"]), int(auth_response["headers"]["x-radiko-keylength"])
    partialkey= auth_key[offset:offset + length]
    partialkey = base64.b64encode(partialkey.encode())
    return [partialkey,authtoken]

def auth2(partialkey, auth_token):
    """ get 2nd auth
    """
    url = "https://radiko.jp/v2/api/auth2"
    headers =  {
                        "X-Radiko-AuthToken": auth_token,
                        "X-Radiko-Partialkey": partialkey,
                        "X-Radiko-User": "dummy_user",
                        "X-Radiko-Device": 'pc'
                    }
    req, res = req_res(url, headers)
    txt = res.read()
    area = txt.decode()
    return area

def give_meta(station, title):
    """ get metadata of programs
    """
    url = 'http://radiko.jp/v2/api/program/station/weekly?station_id={}'.format(station)
    res = requests.get(url ,verify=False)
    res.raise_for_status()
    soup = BeautifulSoup(res.content,"html.parser")
    to_lst = [i.get('to')for i in soup.findAll('prog')]
    # keep only the broadcasted programs
    now = int(re.sub(r'( |-|:)', '', str(dt.now())[:19]))
    to_lst = [time for time in to_lst if now > int(time)]
    
    title_lst = [i.text.replace('\u3000','') for i in soup.findAll('title')][:len(to_lst)]
    mc_lst  = [i.text.replace('\u3000','').replace('/',', ') for i in soup.findAll('pfm')][:len(to_lst)]
    ft_lst = [i.get('ft')for i in soup.findAll('prog')][:len(to_lst)]
    # program date e.g.: 200504
    date_lst = [i.get('ft')[2:8] for i in soup.findAll('prog')][:len(to_lst)]
    # with <br />\n
    info_lst = [re.sub(r'.+</a><br />\n<br />\n', '', i.text.replace('            ', '')) for i in soup.findAll('info')][:len(to_lst)] 
    # program description with <br />\n
    comment_lst = [i.text.replace('\u3000','') for i in soup.findAll('desc')][:len(to_lst)] 
    # for some stations, they give us the description in the "info" tag
    info_lst = [BeautifulSoup(i.text,"html.parser").find(class_="station_content_description").text for i in soup.findAll('info')][:len(to_lst)]
    info_lst = [re.sub(r'( | |\t)*', '', i) for i in info_lst]
    # join
    comment_lst = [a+b for a,b in zip(comment_lst, info_lst)]
    
    arr_title_lst = np.array(title_lst)
    #[i for i in title_lst if re.match(r'.*{}.*'.format(title), i)]
    index = np.where(arr_title_lst == title)[0] 
    if len(index) >= 1:
        ft, to = np.array(ft_lst)[index], np.array(to_lst)[index]
        mc, date, comment = np.array(mc_lst)[index], np.array(date_lst)[index], np.array(comment_lst)[index]
    else:
        ft, to, mc, date, comment = None, None, None, None, None
    return ft, to, mc, date, comment

def get_stations(area, station_id):
    """ get station_name based on station_id
    """
    url = 'http://radiko.jp/v2/station/list/{}.xml'.format(area.split(',')[0])
    res = requests.get(url ,verify=False)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, "html.parser")
    station_id_lst = [i.text for i in soup.findAll('id')]
    station_name_lst = [i.text for i in soup.findAll('name')]
    index = np.where(np.array(station_id_lst)==station_id)[0][0]
    station_name = station_name_lst[index]
    return station_name

def gen_m3u8_url(url, auth_token):
    """ get m3u8 which include a chunk of AAC files
    """
    headers =  {
        "X-Radiko-AuthToken": auth_token,
    }
    req, res = req_res(url, headers)
    body = res.read().decode()
    lines = re.findall('^https?://.+m3u8$' , body, flags=(re.MULTILINE))
    return lines[0]

def simple_title(title):
    """ set manually what you want the names like:
    """
    title = re.sub('(JUNK |…|土曜ワイドラジオTOKYO )', '', title).replace('RaNi Music♪ ','RN2_').replace(' (1)','_1').replace(' (2)','_2').replace('(PART1)', '_1').replace('(PART2)', '_2')
    return title
    
def save(station, title, ft, to, token, mc, date, comment, station_name):
    """ download and save as an .aac file
    aac cant include metadata, so use mp3 style
    """
    comment = comment.replace('<br>','')
    url = f"https://radiko.jp/v2/api/ts/playlist.m3u8?station_id={station}&l=15&ft={ft}&to={to}"
    m3u8 = gen_m3u8_url(url, token)
    title_for_save = simple_title(title)
    filename = '{dt}_{title}'.format(dt=ft[2:8], title=title_for_save)
    # save it as AAC
    shell_scr_to_aac = f"ffmpeg -headers 'X-Radiko-Authtoken:{token}' -i '{m3u8}'  -acodec copy  '{filename}'.aac"
    subprocess.call(shell_scr_to_aac, shell=True)
    # Using ffmpeg, convert AAC to MP3. 
    # ffmpeg can't give a metadata of comment for some reason
    shell_scr_to_mp3 = f"ffmpeg -i '{filename}'.aac -vn -ac 2 -ar 44100 -ab 128k -acodec libmp3lame -f mp3 -metadata date='{date}' -metadata artist='{mc}' -metadata album='{station_name}' '{filename}'.mp3"
    subprocess.call(shell_scr_to_mp3, shell=True)
    # Using eyeD3, give a metadata of comment to MP3
    shell_eyed3 = f"eyeD3 --comment '{comment}' '{filename}'.mp3"
    subprocess.call(shell_eyed3, shell=True)


def main(station, title):
    """ sum of def.
    """
    res = auth1()
    ret = get_partial_key(res)
    partialkey, token = ret[0], ret[1]
    area = auth2(partialkey, token)
    station_name = get_stations(area, station)
    ft_lst, to_lst, mc_lst, date_lst, desc_lst = give_meta(station, title)
    if ft_lst is None:
        pass
    else:
        if len(ft_lst) == 1:
            ft, to, mc, date, desc = ft_lst[0], to_lst[0], mc_lst[0], date_lst[0], desc_lst[0] 
            save(station, title, ft, to, token, mc, date, desc, station_name)
        else:# equal to len(ft_lst) > 1
            for ft, to, mc, date, desc in zip(ft_lst, to_lst, mc_lst, date_lst, desc_lst):
                save(station, title, ft, to, token, mc, date, desc, station_name)

if __name__ == "__main__":
    title_lst_TBS = [
                            'JUNK おぎやはぎのメガネびいき',
                            '土曜ワイドラジオTOKYO ナイツのちゃきちゃき大放送 (1)',
                            '土曜ワイドラジオTOKYO ナイツのちゃきちゃき大放送 (2)',
                            '久米宏 ラジオなんですけど'
                            ]
    for title in title_lst_TBS:
        station = 'TBS'        
        main(station, title)
    ####
    title_lst_FMT = [
                            'Skyrocket Company',
                            'JET STREAM',
                            'Blue Ocean'
                            ]
    for title in title_lst_FMT:
        station = 'FMT'        
        main(station, title)
    ####
    station, title = 'RN2', 'RaNi Music♪ Request Hour'
    main(station, title)
    ####
    station, title = 'FMJ', 'GROOVE LINE'
    main(station, title)
    ####
    title_lst_FMJ = [
                            'SATURDAY NIGHT VIBES',
                            'NIPPON EXPRESS SAUDE! SAUDADE…',
                            'UR LIFESTYLE COLLEGE',
                            'BRIDGESTONE DRIVE TO THE FUTURE',
                            'TRAVELLING WITHOUT MOVING',
                            ]
    for title in title_lst_FMJ:
        station = 'FMJ'        
        main(station, title)
