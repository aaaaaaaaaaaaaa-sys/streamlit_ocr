import streamlit as st
from PIL import Image
import cv2
import easyocr
import json
import numpy as np
import base64
import io

def file_downloader(filename, file_label='File'):
    with open(filename, 'rb') as f:
        data = f.read()

def cv2pil(image):
    new_image = image.copy()
    if new_image.ndim == 2:
        pass
    elif new_image.shape[2] == 3:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

def pil2cv(image):
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:
        pass
    elif new_image.shape[2] == 3:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

st.title("文字認識")

with open('langs.json', mode='rt', encoding='utf-8') as file:
    json_data = json.load(file)

upload_file = st.file_uploader("画像を選択してください",type=['png','jpg'])

if upload_file is not None:
    readimg = Image.open(upload_file)
    w,h = readimg.size
    wsize = 1280
    hsize = 720
    resizeimg = readimg.copy()
    if w > wsize:
        st.warning("この画像は1280x720より大きいためリサイズして表示されます")
        resizeimg = readimg.resize((wsize,hsize))
    elif h > hsize:
        st.warning("この画像は1280x720より大きいためリサイズして表示されます")
        resizeimg = readimg.resize((wsize,hsize))
    else:
       resizeimg = readimg.copy()
    st.image(resizeimg,caption="選択された画像")    

selectlang = st.multiselect("検出する言語を選んでください(必ず対応しているとは限りません)",tuple(json_data.keys()),default="日本語")


donebtn = st.button("実行する")
if donebtn == True:
    if upload_file is not None:
        try:
            langlist = []
            for select in selectlang:
                langlist.append(json_data[select])
            readimg = Image.open(upload_file)
            reader = easyocr.Reader(langlist, gpu=False,download_enabled=True)
            cv2img = pil2cv(readimg)
            h, w, c = cv2img.shape
            wsize = 1280
            hsize = 720
            if w > wsize:
                cv2img = cv2.resize(cv2img,(wsize,hsize))
            elif h > hsize:
                cv2img = cv2.resize(cv2img,(wsize,hsize))
            else:
                pass
            img_gray = cv2.cvtColor(cv2img, cv2.COLOR_BGR2GRAY)
            result = reader.readtext(img_gray,batch_size=3)
            st.write("ここから下が認識結果です")
            for data in result:
                try:
                    st.write(data[1])
                except:
                    pass
                try:
                    cv2.rectangle(cv2img,data[0][0],data[0][2],(0,0,0))
                except:
                    pass
            showimg = cv2pil(cv2img)
            st.image(showimg,caption="OCRした画像")            
            with io.BytesIO() as output:
                showimg.save(output, format='png')
                b64 = base64.b64encode(output.getvalue()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="output.png">download</a>'
                st.markdown(f"ダウンロードする {href}", unsafe_allow_html=True)
        except:
            import traceback
            st.error(traceback.format_exc())
    else:
        st.error("画像を選択してください")