import requests

class Telegram:
    def __init__(self, bot_token, bot_id):
        self.bot_token = bot_token
        self.bot_id = bot_id

    def telegram_bot_sendtext(self, msg):
        send_text = 'https://api.telegram.org/bot' + self.bot_token \
                    + '/sendMessage?chat_id=' + self.bot_id + '&parse_mode=Markdown&text=' + msg

        response = requests.get(send_text)
        return response.json()


# token = '967624914:AAEOGku9Kuud_NudwsLVpvODBgZIY2CIGOA'
# id = '432518661'
# test = Telegram(token, id)
# result = test.telegram_bot_sendtext('testing bot')
# print(result)