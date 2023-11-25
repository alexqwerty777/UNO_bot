import telebot
from telebot import types
from aiogram import Bot, types, Dispatcher, executor
import time
import logging

def get_token():
    with open('TOKEN.txt') as f:
        return f.readline()


TOKEN = get_token()
logging.basicConfig(level=logging.INFO)

# bot = telebot.TeleBot(token=TOKEN)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

players = {}
players_round_points = {}
players_game_points = {}
rounds = {'round_num': 1, 'game_num': 1}
game_run_flag = {}


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, players=players):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id} {user_full_name} {time.asctime()}')
    players[user_id] = user_full_name
    await message.reply(f'Привет, {players.get(user_id)}, ждем подключения остальных игроков...')
    await message.reply(f'Нажмите /begin когда все подключатся')


@dp.message_handler(commands=['end'])
async def start_handler(message: types.Message, players=players,
                        rounds=rounds, players_game_points=players_game_points,
                        players_round_points=players_round_points,
                        game_run_flag=game_run_flag):
    round_num = rounds.get('round_num')
    game_num = rounds.get('game_num')
    game_table = ',\n'.join([f'{players.get(key)}: {value}' for key, value in players_game_points.items()])
    for player in players.keys():
        await bot.send_message(player, text=f'Раунд {round_num} прерван.\n' +
                                            f'Игра {game_num} прервана.\n' +
                                            f'Таблица игры:\n{game_table}')
        await bot.send_message(player, text=f'Для начала новой игры нажми /start')
    rounds['round_num'] = 1
    rounds['game_num'] = 1
    players.clear()
    players_round_points.clear()
    players_game_points.clear()
    game_run_flag.clear()


@dp.message_handler(commands=['begin'])
async def begin_round(message: types.Message,
                        players=players, rounds=rounds,
                        game_run_flag=game_run_flag):
    #start the game
    round_num = rounds.get('round_num')
    game_num = rounds.get('game_num')
    logging.info(f'Start the game: {players} {time.asctime()}')
    game_run_flag[1] = 1
    if players:
        for player in players.keys():
            await bot.send_message(player, text=f'Игра №{game_num}, раунд {round_num} с игроками: {", ".join(players.values())}\n'+
                            'В конце раунда введите кол-во очков одним числом.')
    else:
        await message.answer('Игра не запущена. Нажмите /start для регистрации и дождитесь остальных игроков.')


@dp.message_handler(content_types=['text'])
async def get_points(message: types.Message,
                        players=players,
                        players_round_points=players_round_points,
                        players_game_points=players_game_points,
                        game_run_flag=game_run_flag,
                        rounds=rounds
                     ):

    round_num = rounds.get('round_num')
    game_num = rounds.get('game_num')
    if game_run_flag:
        user_id = message.from_user.id
        if user_id in players.keys():
            try:
                players_round_points[user_id] = int(message.text)
            except:
                await  message.reply('Некорректное значение')
        else:
            await  message.reply('Вы не в игре')

        #all players wrote points
        if players.keys() == players_round_points.keys():
            if not 'x' in players_round_points.values():
                for key, value in players_round_points.items():
                    if key in players_game_points.keys():
                        players_game_points[key] = players_game_points.get(key) + value
                    else:
                        players_game_points[key] = value

                for key in players_round_points.keys():
                    players_round_points[key] = 'x'

                #check finish game
                max_value = max(players_game_points.values())
                if max_value > 499:
                    loosers = {id: point for id,point in players_game_points.items() if point == max_value}
                    if len(loosers.keys()) > 1:
                        loosers_str = ',\n'.join([f'{players.get(key)}: {value}' for key, value in loosers.items()])
                        game_table = ',\n'.join([f'{players.get(key)}: {value}' for key, value in loosers.items()])
                        for player in players.keys():
                            await bot.send_message(player, text=f'Раунд {round_num} завершен.\n'+
                                            f'Игра {game_num} завершена. Проиграли игроки {loosers_str}\n'+
                                            f'Таблица игры:\n{game_table}')

                    else:
                        l_name = players.get([k for k in loosers.keys()][0])
                        l_points = [v for v in loosers.values()][0]
                        game_table = ',\n'.join([f'{players.get(key)}: {value}' for key, value in players_game_points.items()])

                        for player in players.keys():
                            await bot.send_message(player, text=f'Раунд {round_num} завершен.\n' +
                                            f'Игра {game_num} завершена.\n' +
                                            f'Проиграл игрок {l_name}' +
                                            f' - {l_points} очков\n'+
                                            f'Таблица игры:\n{game_table}')
                            await bot.send_message(player, text=f'Для начала следующей игры нажми /begin')

                    for id in players_game_points.keys():
                        players_game_points[id] = 0
                    rounds['game_num'] = game_num + 1
                    rounds['round_num'] = 1

                else:
                    #end this round and start the next
                    points_str = '\n'.join([f'{players.get(key)}: {value}' for key, value in players_game_points.items()])
                    for player in players.keys():
                        await bot.send_message(player, text=f'Раунд {str(round_num)} завершен.\n' + points_str)
                        await bot.send_message(player, text=f'Начинаем раунд {round_num + 1}')
                    rounds['round_num'] = round_num + 1

    else:
        await message.answer('Игра не запущена. Нажмите /start для регистрации и дождитесь остальных игроков.')


if __name__ == '__main__':
    executor.start_polling(dp)


