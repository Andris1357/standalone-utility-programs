# REQUIRES HAVING AN ACCOUNT CREATED TO RECEIVE A DEVELOPER KEY; STD USER ELIGIBLE FOR ABOUT 10K CALLS/DAY | 1 call = 1 dict

# SHELL:
    # "touch channels_hist_gcp_fin.csv"
    # AFTER HAVING IMPORTED .PY FILE MANUALLY (UI HAS SUPPORT FOR THIS) -> "nohup python3 main.py"
    # LATER CHECK WITH ßnano
    # TO KILL:
        # "ps -ef |grep nohup" -> find PID
        # "kill [PID]"
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import time
import schedule
import csv

load_ids = ['UCqK_GSMbpiV8spgD3ZGloSw', 'UCYYIPdro1FZ6Wc5nJOn0CpA', 'UC1usFRN4LCMcfIV7UjHNuQg', 'UC606MUq45P3zFLa4VGKbxsg', 'UCEAZeUIeJs0IjQiqTCdVSIg',
            'UCc35WvHmQjLE8NN4Y_ITmUQ', 'UCbLhGKVY-bJPcawebgtNfbw', 'UC606MUq45P3zFLa4VGKbxsg', 'UCVhQ2NnY5Rskt6UjCUkJ_DA', 'UC7_gcs09iThXybpVgjHZ_7g',
           'UCYO_jab_esuFRV4b17AJtAw', 'UCR1IuLEqb6UEA_zQ81kwXfg', 'UCmh7afBz-uWwOSSNTqUBAhg', 'UCSv7zzf9wjmqMnk6zzN5gYQ', 'UCdTGUj9Py1UtLMz-SyxAI0g',
          'UCciQ8wFcVoIIMi-lfu8-cjQ', 'UCfMiRVQJuTj3NpZZP1tKShQ', 'UCBH5VZE_Y4F3CMcPIzPEB5A', 'UC_0eFMbKBNkMBSk3NWQSIFA', 'UCGy7SkBjcIAgTiwkXEtPnYg',
          'UCYOHtOzMZGwXBLZX1Ltf78g', 'UC32oVb-nfyRBNlWzUw3dC5Q', 'UC4oy8Ur_mAeDjSO6Fwj8GMg', 'UCsooa4yRKGN_zEE8iknghZA', 'UC5nc_ZtjKW1htCVZVRxlQAQ',
         'UCtxJFU9DgUhfr2J2bveCHkQ', 'UCJFp8uSYCjXOMnkUyb3CQ3Q', 'UCgNg3vwj3xt7QOrcIDaHdFg', 'UCIEv3lZ_tNXHzL3ox-_uUGQ', 'UCxDZs_ltFFvn0FDHT6kmoXA',
         'UC9WQRw8jgJhag-vkDNTDMRg', 'UCoLUji8TYrgDy74_iiazvYA', 'UCrdWRLq10OHuy7HmSckV3Vg', 'UCRzgK52MmetD9aG8pDOID3g', 'UCO5QSoES5yn2Dw7YixDYT5Q',
         'UC5YKivGUTTQmhSuaXbxfZSg', 'UCDgUAAHgsV2fFZQm2fIWBnA', 'UCnZx--LpG2spgmlxOcC-DRA', 'UCQU2q2zY1oejRRzK66fIAzA', 'UCQAvjhqp559qSQx2dcg9WVg',
        'UCorrTSqD41oRv3_6yIixWjw', 'UCvJJ_dzjViJCoLf5uKUTwoA', 'UCzaQpnAyt-IHT7MKgT2WhaA', 'UCn6pE6gt_rMnxcb1YjG4a9Q', 'UCcmZHsuUt_DOzcgIcLd0Qnw',
        'UCvjgXvBlbQiydffZU7m1_aw', 'UCRvqjQPSeaWn-uEx-w0XOIg', 'UCrrygkv8lOqCt905OesqfDQ', 'UC6nSFpj9HTCZ5t-N3Rm3-HA', 'UCRlICXvO4XR4HMeEB9JjDlA', 'UCs6nmQViDpUw0nuIx9c_WvA']
load_ids = set(load_ids)

def input_i():
    youtube = build('youtube', 'v3',
                        developerKey='???') # MASKED: MY DEVELOPER KEY, REQUIRES REGISTRATION TO THIS GFEATURE OF GOOGLE SEPARATELY
    obj_out = []

    for id_in in load_ids:  
        ch_request = youtube.channels().list(
            part = 'statistics, snippet',
            id = id_in)

        ch_response = ch_request.execute()
 
        sub = ch_response['items'][0]['statistics']['subscriberCount']
        vid = ch_response['items'][0]['statistics']['videoCount']
        views = ch_response['items'][0]['statistics']['viewCount']
        name = ch_response['items'][0]['snippet']['localized']['title']

        channel_i = [id_in, name, sub, views, vid, datetime.now()]
        obj_out.append(channel_i)

    with open("channels_hist_gcp_fin.csv", 'a+', newline='', encoding='UTF8') as f:
      
        writer = csv.writer(f)
        for ch_stats in obj_out:
            row = ch_stats
            writer.writerow(row)
        
        #install google lib: <pip3|pip install google-api-python-client>
    print(f"batch done at {datetime.now()}")

schedule.every(2).hours.do(lambda: input_i)
while True:
    schedule.run_pending()
    