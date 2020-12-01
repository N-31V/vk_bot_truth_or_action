import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import pymysql.cursors
import requests
import random
import pandas as pd
import numpy as np

pilid_list = []
vk_session = vk_api.VkApi(token="d7422c47658d2389d8aa3c705e039dfe8c237931135f68b787b8b468ea4aed236eeed3170bec567446009")
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, "196155794")
questions = pd.read_csv('questions.csv', sep=';')
actions = pd.read_csv('actions.csv', sep=';')
player = 0
question = ''
action = ''

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:
        print(event)
        # проверяем пришло сообщение от пользователя или нет
        if event.from_user:
            print(event.object)
            print('from user {}: {}'.format(event.object.message['from_id'], event.object.message['text']))
            vk.messages.send(peer_id=event.object.message['from_id'], random_id=get_random_id(),
                             message=event.object.message['text'])

        else:
            mess = event.object.message['text'].lower().split(' ')
            author = event.object.message['from_id']
            chat_id = event.object.message['peer_id']
            if mess[0] == 'пилид' or mess[0] == 'пд':
                if len(mess) == 2 and (mess[1] == 'команды' or mess[1] == 'инфо'):
                    str = 'Команды:\n\n' \
                    '"пилид команды" (или "пд инфо") — выводит возможные команды\n' \
                    '"пилид играю" — устанавливает статус в игре\n' \
                    '"пилид не играю" — устанавливает статус вне игры\n' \
                    '"пилид играют?" — выводит список игроков\n' \
                    '"пилид следующий" (или "пд кто") — выбирает, кому переходит ход\n' \
                    '"пилид кого(кому)" — применяется, когда необходимо выбрать с кем произвести действие\n' \
                    '"пилид правда" или "пилид действие" -- ответ на мой запрос.\n \n' \
                    'Ход игры: \n\n игроки указывают своё участие в игре при помощи команды "пд играю", затем выбирается ' \
                          'первый игрок при помощи команды "пд следующий", выбранный игрок выбирает "пд правда" или ' \
                          '"пд действие", завершая ход игрок выбирает следующего: "пд следующий" '
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)
                elif len(mess) == 2 and mess[1] == 'играю':
                    if pilid_list.count(author) == 0:
                        pilid_list.append(author)
                    print(pilid_list)
                    str = '{} играет в ПилиД'.format(vk.users.get(user_ids=author)[0]['first_name'])
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)
                elif len(mess) == 2 and mess[1] == 'играют?':
                    if len(pilid_list) > 0:
                        str = ''
                        for p in pilid_list:
                            str += '@id{} ({} {}), '.format(p, vk.users.get(user_ids=p)[0]['first_name'], vk.users.get(user_ids=p)[0]['last_name'])
                    else:
                        str = 'Со мной никто не играет :с'
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)
                elif len(mess) == 3 and mess[1] == 'не' and mess[2] == 'играю':
                    if pilid_list.count(author) != 0:
                        pilid_list.remove(author)
                    print(pilid_list)
                    str = '{} не играет в ПилиД'.format(vk.users.get(user_ids=author)[0]['first_name'])
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)
                elif len(mess) == 2 and (mess[1] == 'кто' or mess[1] == 'следующий'):
                    try:
                        player = random.choice(pilid_list)
                        print(player)
                        str = '@id{} ({}), правда или действие?'.format(player,
                                                                        vk.users.get(user_ids=player)[0]['first_name'])
                    except:
                        str = 'Со мной никто не играет :с'
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)

                elif len(mess) == 2 and (mess[1] == 'кого' or mess[1] == 'кому'):
                    try:
                        pilid_list.remove(player)
                        player2 = random.choice(pilid_list)
                        print(player2)
                        str = 'думаю, это будет {} {}'.format(vk.users.get(user_ids=player2)[0]['first_name'], vk.users.get(user_ids=player2)[0]['last_name'])
                    except:
                        str = 'Больше никого нет ('
                    finally:
                        pilid_list.append(player)
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)

                elif len(mess) == 2 and mess[1] == 'правда' and author == player:
                    question = random.choice(questions['Вопросы'])
                    str = '{}, {}'.format(vk.users.get(user_ids=player)[0]['first_name'], question)
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)

                elif len(mess) == 2 and mess[1] == 'действие' and author == player:
                    action = random.choice(actions['Действия'])
                    str = '{}, {}'.format(vk.users.get(user_ids=player)[0]['first_name'], action)
                    vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)

                elif len(mess) == 3 and mess[1] == 'удалить':
                    if mess[2] == 'вопрос':
                        questions = questions.loc[questions['Вопросы'] != question]
                        questions.to_csv('questions.csv', index=False)
                        str = 'удалено: {}'.format(question)
                        vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)

                    if mess[2] == 'действие':
                        actions = actions.loc[actions['Действия'] != action]
                        actions.to_csv('actions.csv', index=False)
                        str = 'удалено: {}'.format(action)
                        vk.messages.send(peer_id=chat_id, random_id=get_random_id(), message=str)
