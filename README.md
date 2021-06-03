# Конвертер бот
Этот бот был создан, чтобы упростить конвертацию обычных изображений в один ПДФ файл. 

## Как работает бот
__Короткая версия: (bold)__  
1)Пользователь отправляет фотографии в Вконтакте  
2)Пользователь отправляет сообщение "Pdf" для активации бота  
3)Пользователь пишет в новом сообщении нужное название документа и количество фотографий  
4)Бот качает фотографии и конвертирует их     
5)Бот загружает на сервера документ, а потом отправляет его  

__Полная версия: (bold)__

В полной версии будут разобраны основные _уникальные_ части бота. 

Функция, которая представлена ниже, используется для получения всех вложений из диалога.  
Также стоит отметить, что из всех фотографий выбираются только те, которые имеют наилучшее качество.   
```
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
    ...
```
При конвертации изображений используется популярная библиотека PIL:  
```result[0].save("Photo_vk" + '\\' + name_of_pdf + '.pdf', save_all=True, append_images=result[1:len(list)])```  
В метод .save передаются название документа и изображения, которые в нем должны находится.

Для того, чтобы загрузить документ на сервера ВК, нужно следовать подробной [инструкции](https://vk.com/dev/upload_files_2?f=10.%2BЗагрузка%2Bдокументов), которая выложена на официальной странице ВК.  
Ниже можно увидеть готовый вариант:
```
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
```
Далее готовый документ отправляется пользователю.

## Пример работы и возможности для улучшения 

Пример работы бота:  

![Пример](https://user-images.githubusercontent.com/83017027/120692893-078f0100-c4b1-11eb-929d-6abb29ea3ace.png)

Вариант улучшения:  
Если изображение поступает в плохом качестве, то нейронная сеть будет улучшать фотографии.
