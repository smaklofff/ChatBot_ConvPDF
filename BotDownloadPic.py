import requests
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
import img2pdf
import urllib.request
import PIL
import os
import random
import json
import re


def get_history(peer_id, amount):
    """Получение истории сообщений"""
    history = vk.messages.getHistory(count=3,
                                     user_id=peer_id)
    'Проверка типа вложения'
    if history['items'][2]['attachments'][0]['type'] == 'photo':
        media_type = 'photo'
    else:
        media_type = 'doc'
    'Получение вложений'
    photo = vk.messages.getHistoryAttachments(
        peer_id=peer_id,
        media_type=media_type,
        count=amount,
        preserve_order=1)

    "Выбор наилучшего качества изображения"
    list_photo = []
    link = ''
    for i in range(len(photo['items'])):
        if media_type == 'photo':
            short = photo['items'][i]['attachment']['photo']['sizes']
            max_size = 0
            for j in range(len(short)):
                if max_size < short[j]['height'] * short[j]['width']:
                    max_size = short[j]['height'] * short[j]['width']
                    link = short[j]['url']
            list_photo.append(link)
        else:
            list_photo.append(photo['items'][i]['attachment']['doc']['url'])

    return list_photo


def save_picture(list_photo, name):
    """Чистка папки"""
    for the_file in os.listdir("Photo_vk"):
        file_path = os.path.join("Photo_vk", the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    '''Сохранение картинок jpg в формате pdf'''
    for i in range(len(list_photo)):
        img = urllib.request.urlopen(list_photo[i]).read()
        out = open("Photo_vk\\" + name + '_' + str(i) + ".jpg", "wb")
        out.write(img)
        out.close


def information_about_the_document(user_id, name):
    """Загрузка документа на сервера вк"""

    'Получение ссылки для загрузки вложения'
    upload_url_document = vk.docs.getMessagesUploadServer(type='doc',
                                                          peer_id=user_id)['upload_url']
    'Обработка ответа'
    request = requests.post(upload_url_document,
                            files={'file': open('Photo_vk\\' + name + '.pdf', 'rb')}).json()['file']

    'Получение данных о документе, который был сохранен на сервере'
    document_information = vk.docs.save(file=request,
                                        title=name)
    document_information = 'doc' + str(document_information['doc']['owner_id']) + '_' + str(document_information['doc']['id'])
    'Отправка документа'
    send_msg(user_id, 'Вот твой PDF', document_information)


def convert_to_pdf(name_of_pdf):
    """Конвертация изображения в пдф"""
    list, result, = [], []
    for x, y, files in os.walk('Photo_vk'):
        list.extend(files)
    for i in range(len(list)):
        image = PIL.Image.open("Photo_vk" + '\\' + list[i]).convert('RGB')
        im = image.convert('RGB')
        result.append(im)
    result[0].save("Photo_vk" + '\\' + name_of_pdf + '.pdf', save_all=True, append_images=result[1:len(list)])


def send_msg(user_id, txt, attachment):
    mess_id = random.randint(0, 3000000000000)
    vk.messages.send(
        user_id=user_id,
        random_id=mess_id,
        attachment=attachment,
        message=txt)


def login(access_token):
    """Авторизация"""
    vk_session = vk_api.VkApi(token=access_token)
    return vk_session.get_api(), VkUpload(vk_session), vk_session, VkLongPoll(vk_session)


def main():
    requests.Session()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            proverka = event.user_id
            if event.to_me:
                text = event.text.lower()
                if text == 'pdf':
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.user_id == proverka:
                            if event.to_me:
                                try:
                                    list_text = event.text.lower().split(',')
                                    save_picture(get_history(event.user_id, int(list_text[1])), 'Picture')
                                    convert_to_pdf(list_text[0])
                                    information_about_the_document(event.user_id, list_text[0])
                                except:
                                    pass

                                break


if __name__ == "__main__":
    vk, upload, vk_session, longpoll = login(
        '*********************')
    main()

