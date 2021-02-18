from flask import Flask, request, abort
import os
import pickle
import re
from random import shuffle
import glob

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, URIAction,
    responses, MemberIds, CarouselColumn, CarouselTemplate,
    PostbackAction, MessageAction, URIAction, ImageCarouselColumn, ImageCarouselTemplate
)
from get_url import image_urls


app = Flask(__name__)

#環境変数取得
# 犯人は踊る
YOUR_CHANNEL_ACCESS_TOKEN = "lddZVDy+pjNCPe1Zu/igEyY/9/tBZ1jaokCSIVCKv4lMwn8cB3RYU4KSk5OKI8wIpAuP84O1LxGz/3EmvCcj1qcVGfbenAwJLJEzrQVXhavXy8dcRZdEbwLSONEaKM0Gv2ES6BnvdpkJntwEySlgQAdB04t89/1O/w1cDnyilFU="
YOUR_CHANNEL_SECRET = "088336230fa1d600499669231f6590be"
owner_id = "U4a91bdd11f17b03c08567d9770979fb5"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# http://s2.upup.be/lQEtTRWfpg
# http://s2.upup.be/6cWTS19Jd0

class Cards:
    info = [
        ["第一発見者", 1, "このカードを出してゲームを始める。\n今回起こった事件を考えて全員に伝えよう。", image_urls[1][0], image_urls[1][1]],
        ["犯人", 1, "探偵に当てられてしまうと敗け。\n最後の手札1枚のときだけ出せる。出せたなら勝ち。", image_urls[2][0], image_urls[2][1]],
        ["探偵", 4, "他のだれか1人に\n｢あなたが犯人ですね？｣と聞く。\n当たれば勝ち。\n2周目になるまでは使えない。", image_urls[3][0], image_urls[3][1]],
        ["アリバイ", 5, "手札にあれば、\n｢犯人ではありません。｣と\n答えられる。\n出しても何も起きない。", image_urls[4][0], image_urls[4][1]],
        ["たくらみ", 2, "出すと、犯人の味方になる。\n犯人が勝つと、同じく勝ち。\n犯人が敗けると、同じく敗け。", image_urls[5][0], image_urls[5][1]],
        ["情報操作", 3, "全員、自分の左どなりの人に手札の1枚をこっそりわたす。", image_urls[6][0], image_urls[6][1]],
        ["うわさ", 4, "全員、自分の右どなりの人の手札からこっそり1枚ひく。", image_urls[7][0], image_urls[7][1]],
        ["目撃者", 3, "他のだれか1人の手札をこっそりぜんぶ見せてもらう。", image_urls[8][0], image_urls[8][1]],
        ["少年", 1, "他全員に指示して犯人を知る。\n①｢はいみなさん目を閉じて｣\n②｢犯人カードを持っている人は目をあけて｣\n③｢みなさん、目をあけて｣", image_urls[9][0], image_urls[9][1]],
        ["いぬ", 1, "他のだれか1人の手札を1枚選ぶ。\n選んだカードを全員に見せる。\nそのカードが犯人なら勝ち。\n犯人でないならもとにもどす。", image_urls[10][0], image_urls[10][1]],
        ["取り引き", 5, "他のだれか1人と、手札の1枚をこっそり交換しあう。\n(手札がないなら交換しない)", image_urls[11][0], image_urls[11][1]],
        ["一般人", 2, "出しても何も起きない。", image_urls[12][0], image_urls[12][1]]
    ]

    def __init__(self, index):
        self.name = Cards.info[index][0]
        self.num_of_cards = Cards.info[index][1]
        self.explain = self.name + ("ー"*(10 - len(self.name))) + "\n" + Cards.info[index][2]
        self.url = Cards.info[index][3]
        self.url_red = Cards.info[index][4]

    def __repr__(self):
        return self.name

class Deck:
    # OK
    def __init__(self):
        self.cards = []
        self.using_cards = []
        for i, info in enumerate(Cards.info):
            for j in range(info[1]):
                self.cards.append(Cards(i))
    # OK
    def make_using_cards(self, message, num_players):
        num_using_cars = num_players * 4
        if message == "「おまかせ」を選択":
            shuffle(self.cards)
            rest_num_card = num_using_cars - len(self.using_cards)
            for i in range(rest_num_card):
                self.using_cards.append(self.cards.pop())
            now_cards = []
            for card in self.using_cards:
                now_cards.append(card.name)
            replay = "【今回の使用カード】\n" + "\n".join(now_cards)
            return replay
        else:
            choiced_card = message[1:-8]
            for i, card in enumerate(Cards.info):
                if choiced_card == card[0]:
                    add_card_index = i
            add_card_name = Cards.info[add_card_index][0]
            pick_up = next((card for card in self.cards if card.name == add_card_name), None)
            try:
                self.cards.remove(pick_up)
                self.using_cards.append(pick_up)
                replay = "{}を追加しました".format(choiced_card)
                return replay
            except:
                replay = "もうありません別のカードを指定してください"
                return replay

class Player:
    # OK
    def __init__(self, name, user_id):
        self.name = name
        self.id = user_id
        self.hand_cards = []
        self.wins = 0
        self.turn = 0

class Game:
    # OK
    def __init__(self, players_profile, group_id):
        self.players = []
        for player in players_profile:
            self.players.append(Player(player["display_name"], player["user_id"]))
        self.deck = Deck()
        self.now_turn = 0
        self.id = group_id
        self.make_hand_cards = False

        self.this_turn_process = "not_yet" # or "done"
        self.this_turn_process_all = []
        self.this_turn_process_players = len(self.players)
        # self.deck.make_using_cards(4)
        # self.deck.make_hands()
    def make_hands(self):
        shuffle(self.deck.using_cards)
        for i in range(4):
            for p in self.players:
                p.hand_cards.append(self.deck.using_cards.pop())

def read_data(event):
    send_id = event.source.sender_id
    with open("game{}.binaryfile".format(send_id), "rb") as f:
        this_game = pickle.load(f)
    return this_game

def save_data(this_game):
    with open("game{}.binaryfile".format(this_game.id), "wb") as f:
        pickle.dump(this_game, f)
    for player in this_game.players:
        with open("game{}.binaryfile".format(player.id), "wb") as f:
            pickle.dump(this_game, f)



def cards_carousel(group_id):
    kind_cards = ["第一発見者","犯人","探偵","アリバイ","たくらみ","情報操作","うわさ","目撃者","少年","いぬ","取り引き","一般人"]
    line_bot_api.push_message(
        group_id,
        TemplateSendMessage(
            alt_text='使用するカードを選択',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='カード選択',
                        text='使用するカードを選択\n複数回可',
                        actions=[
                            MessageAction(label=kind_cards[0],text="「{}」をデッキに追加".format(kind_cards[0])),
                            MessageAction(label=kind_cards[1],text="「{}」をデッキに追加".format(kind_cards[1])),
                            MessageAction(label=kind_cards[2],text="「{}」をデッキに追加".format(kind_cards[2])),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='カード選択',
                        text='使用するカードを選択\n複数回可',
                        actions=[
                            MessageAction(label=kind_cards[3],text="「{}」をデッキに追加".format(kind_cards[3])),
                            MessageAction(label=kind_cards[4],text="「{}」をデッキに追加".format(kind_cards[4])),
                            MessageAction(label=kind_cards[5],text="「{}」をデッキに追加".format(kind_cards[5])),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='カード選択',
                        text='使用するカードを選択\n複数回可',
                        actions=[
                            MessageAction(label=kind_cards[6],text="「{}」をデッキに追加".format(kind_cards[6])),
                            MessageAction(label=kind_cards[7],text="「{}」をデッキに追加".format(kind_cards[7])),
                            MessageAction(label=kind_cards[8],text="「{}」をデッキに追加".format(kind_cards[8])),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='カード選択',
                        text='使用するカードを選択\n複数回可',
                        actions=[
                            MessageAction(label=kind_cards[9],text="「{}」をデッキに追加".format(kind_cards[9])),
                            MessageAction(label=kind_cards[10],text="「{}」をデッキに追加".format(kind_cards[10])),
                            MessageAction(label=kind_cards[11],text="「{}」をデッキに追加".format(kind_cards[11])),
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='カード選択',
                        text='使用するカードを選択\n複数回可',
                        actions=[
                            MessageAction(label="おまかせ",text="「おまかせ」を選択"),
                            MessageAction(label="説明をみる",text="カードの説明が欲しいな"),
                            MessageAction(label="現在のデッキを確認",text="今のゲームデッキを教えて")
                        ]
                    )
                ]
            )
        )
    )


def game_set(group_id):
    with open("players{}.binaryfile".format(group_id), "rb") as f:
        players_profile = pickle.load(f)
    this_game = Game(players_profile, group_id)
    return this_game

def cards_explain():
    cards_info = []
    for card in Cards.info:
        cards_info.append(card[0] + " {}枚\n".format(card[1]) + card[2])
    explain = "\n\n".join(cards_info)
    return "【カード一覧】\n" + explain

def send_card(player_class, back=False):
    user_id = player_class.id
    cards = player_class.hand_cards
    shuffle(cards)
    card_back_url = image_urls[0][1]
    columns = []
    if back == False:
        for card in cards:
            columns.append(ImageCarouselColumn(image_url=card.url,action=MessageAction(label=card.name, text=card.explain)))
    else:
        for card in cards:
            columns.append(ImageCarouselColumn(image_url=card_back_url,action=MessageAction(label="？？？", text=card.name)))
    line_bot_api.push_message(user_id, TemplateSendMessage(alt_text="手札",template=ImageCarouselTemplate(columns=columns)))

def first_open_cards(game):
    turn = [i for i in range(1, len(game.players))]
    shuffle(turn)
    for player in game.players:
        send_card(player)
        send_message = []
        cards = []
        for card in player.hand_cards:
            cards.append(card.name)
        if "第一発見者" in cards:
            player.turn = 0
            send_message = "第一発見者はあなたです。あなたから事件は始まります。"
        else:
            player.turn = turn.pop()
            send_message = "あなたの順番は{}番目です。".format(player.turn + 1)
        line_bot_api.push_message(player.id, TextSendMessage(text=send_message))

def this_turn_player_and_lap(this_game):
    this_turn_player_class = this_game.players[this_game.now_turn % len(this_game.players)]
    this_lap = this_game.now_turn // len(this_game.players)
    return [this_turn_player_class, this_lap]

def next_game(this_game):
    this_turn_player_class = this_turn_player_and_lap(this_game)[0]
    this_lap = this_turn_player_and_lap(this_game)[1]
    if this_game.this_turn_process == "done":
        line_bot_api.push_message(this_game.id, TemplateSendMessage(
            alt_text="次のターンへ",
            template=ButtonsTemplate(
                text="次のターンへ進むときにこちらを押してください",
                title="{}ターン目{}".format(str(this_lap + 1), this_turn_player_class.name),
                actions=[MessageAction(
                    label="次へ進む",
                    text="{}ターン目「{}」の番は終わったから次のターンに進めて".format(this_lap + 1, this_turn_player_class.name))
                ])))


def decide_send_card(player_class, this_lap, event):
    user_id = player_class.id
    cards = player_class.hand_cards
    shuffle(cards)
    columns = []
    for card in cards:
        columns.append(ImageCarouselColumn(image_url=card.url_red,action=MessageAction(label=card.name, text="{}ターン目\n「{}」を場に出す".format(this_lap + 1, card.name))))
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="以下から出すカードを選んでください。（変更はできません）"))
    line_bot_api.push_message(user_id, TemplateSendMessage(alt_text="手札",template=ImageCarouselTemplate(columns=columns)))

def remove_card_form_player(card_class, player_class):
    player_class.hand_cards.remove(card_class)

def remove_card_name_from_player(card_name, player_class):
    remove_card_class = next((card for card in player_class.hand_cards if card.name == card_name), None)
    remove_card_form_player(remove_card_class, player_class)
    return remove_card_class

def add_card_name_to_player(card_name, player_class):
    add_card_list_index = [i for i in range(len(Cards.info)) if Cards.info[i][0] == card_name][0]
    player_class.hand_cards.append(Cards(add_card_list_index))

def finish_game(this_game):
    line_bot_api.push_message(this_game.id, TextSendMessage(text="【ゲーム終了】\nゲームが終了しました。設定をリセットします"))
    ids = [player.id for player in this_game.players]
    ids.append(this_game.id)
    file_list = [glob.glob("*{}*".format(ID)) for ID in ids]
    for filename in file_list:
        os.remove(filename)

    line_bot_api.push_message(this_game.id, TextSendMessage(text="以下のファイルを削除します。\n" + "\n".join(file_list)))

def card_action(take_out_card_name, this_game, this_turn_player_class):
    text_send_message = TextSendMessage(text="{}さんが「{}」カードを出しました。\nカードの指示に従ってください".format(this_turn_player_class.name, take_out_card_name))
    if take_out_card_name == "第一発見者":
        line_bot_api.push_message(this_game.id, text_send_message)
        this_game.this_turn_process = "done"

    elif take_out_card_name == "犯人":
        line_bot_api.push_message(this_game.id, TextSendMessage(text="{}さんが「{}」カードを出しました。\nおめでとうございます。{}さんと「たくらみ」カードを出した人の勝ちです。見事犯人を隠し通しました".format(this_turn_player_class.name, take_out_card_name, this_turn_player_class.name)))
        finish_game(this_game.id)

    elif take_out_card_name == "探偵":
        line_bot_api.push_message(this_game.id, text_send_message)
        names = [player for player in this_game.players if player.name != this_turn_player_class.name]
        names = [player.name for player in names if len(player.hand_cards) > 0]
        actions = [MessageAction(label="{}".format(name), text="{}を疑う".format(name)) for name in names]

        actions.reverse()
        num_last_column_actions = len(actions) % 3
        if num_last_column_actions == 0:
            num_columns = len(actions) // 3
        else:
            num_columns = len(actions) // 3 + 1

        columns = []
        for i in range(num_columns):
            if i == num_columns - 1:
                this_actions = actions[i * 3:]
                while len(this_actions) < 3:
                    this_actions.append(MessageAction(label="無効", text="これは無効です"))
            else:
                this_actions = actions[i * 3 : i * 3 + 3]

            this_column = CarouselColumn(thumbnail_image_url=None,title="【探偵】犯人はお前だ！",text="疑う人を選んでください",actions=this_actions)
            columns.append(this_column)

        line_bot_api.push_message(this_turn_player_class.id, TemplateSendMessage(alt_text="誰を疑う？", template=CarouselTemplate(columns=columns)))





    elif take_out_card_name == "アリバイ":
        line_bot_api.push_message(this_game.id, TextSendMessage(text="何も起きなかった"))
        this_game.this_turn_process = "done"

    elif take_out_card_name == "たくらみ":
        line_bot_api.push_message(this_game.id, TextSendMessage(text="{}は犯人の味方になった".format(this_turn_player_class.name)))
        this_game.this_turn_process = "done"

    elif take_out_card_name == "情報操作":
        line_bot_api.push_message(this_game.id, text_send_message)
        for player in this_game.players:
            if len(player.hand_cards) > 0:
                give_card_for = this_game.players[ (player.turn + 1) % len(this_game.players) ].name
                line_bot_api.push_message(player.id, TextSendMessage(text="以下のカードから左隣の人、{}に渡すカードを選んでください".format(give_card_for)))
                columns = []
                for card in player.hand_cards:
                    columns.append(ImageCarouselColumn(image_url=card.url_red,action=MessageAction(label=card.name, text="「{}」を「{}」に渡します".format(card.name, give_card_for))))
                line_bot_api.push_message(player.id, TemplateSendMessage(alt_text="手札",template=ImageCarouselTemplate(columns=columns)))
            else:
                this_game.this_turn_process_players -= 1
                line_bot_api.push_message(player.id, TextSendMessage(text="カードがないので渡せません。待機していてください。"))
                save_data(this_game)

    elif take_out_card_name == "うわさ":
        hide_url = image_urls[0][1]
        line_bot_api.push_message(this_game.id, text_send_message)
        for player in this_game.players:
            take_card_from = this_game.players[ (player.turn - 1) % len(this_game.players) ]
            if len(take_card_from.hand_cards) > 0:
                line_bot_api.push_message(player.id, TextSendMessage(text="以下のカードから右隣の人、{}からもらうカードを選んでください".format(take_card_from.name)))
                columns = []
                for card in take_card_from.hand_cards:
                    columns.append(ImageCarouselColumn(image_url=hide_url,action=MessageAction(label="？？？", text="「{}」を「{}」からもらいました".format(card.name, take_card_from.name))))
                line_bot_api.push_message(player.id, TemplateSendMessage(alt_text="右隣の人の手札",template=ImageCarouselTemplate(columns=columns)))
            else:
                line_bot_api.push_message(player.id, TextSendMessage(text="対象の人のカードがありませんでした。待機していてください"))
                this_game.this_turn_process_players -= 1

    elif take_out_card_name == "目撃者":
        line_bot_api.push_message(this_game.id, text_send_message)
        names = [player for player in this_game.players if player.name != this_turn_player_class.name]
        names = [player.name for player in names if len(player.hand_cards) > 0]
        actions = [MessageAction(label="{}".format(name), text="{}のカードをみる".format(name)) for name in names]

        num_last_column_actions = len(actions) % 3
        if num_last_column_actions == 0:
            num_columns = len(actions) // 3
        else:
            num_columns = len(actions) // 3 + 1

        columns = []
        for i in range(num_columns):
            if i == num_columns - 1:
                this_actions = actions[i * 3:]
                while len(this_actions) < 3:
                    this_actions.append(MessageAction(label="無効", text="これは無効です"))
            else:
                this_actions = actions[i * 3 : i * 3 + 3]

            this_column = CarouselColumn(thumbnail_image_url=None,title="【目撃者】おれはみた！",text="カードをみる人を選んでください",actions=this_actions)
            columns.append(this_column)

        line_bot_api.push_message(this_turn_player_class.id, TemplateSendMessage(alt_text="誰のカードをみる？", template=CarouselTemplate(columns=columns)))

    elif take_out_card_name == "少年":
        line_bot_api.push_message(this_game.id, text_send_message)
        this_game.this_turn_process = "done"

    elif take_out_card_name == "いぬ":
        line_bot_api.push_message(this_game.id, text_send_message)
        names = [player for player in this_game.players if player.name != this_turn_player_class.name]
        names = [player.name for player in names if len(player.hand_cards) > 0]
        actions = [MessageAction(label="{}".format(name), text="{}から怪しい匂いがする".format(name)) for name in names]
        num_last_column_actions = len(actions) % 3
        if num_last_column_actions == 0:
            num_columns = len(actions) // 3
        else:
            num_columns = len(actions) // 3 + 1

        columns = []
        for i in range(num_columns):
            if i == num_columns - 1:
                this_actions = actions[i * 3:]
                while len(this_actions) < 3:
                    this_actions.append(MessageAction(label="無効", text="これは無効です"))
            else:
                this_actions = actions[i * 3 : i * 3 + 3]

            this_column = CarouselColumn(thumbnail_image_url=None,title="【いぬ】怪しい匂いがするぞ？",text="疑う人を選んでください",actions=this_actions)
            columns.append(this_column)

        line_bot_api.push_message(this_turn_player_class.id, TemplateSendMessage(alt_text="誰を疑う？", template=CarouselTemplate(columns=columns)))




    elif take_out_card_name == "取り引き":
        line_bot_api.push_message(this_game.id, text_send_message)
        names = [player for player in this_game.players if player.name != this_turn_player_class.name]
        names = [player.name for player in names if len(player.hand_cards) > 0]
        actions = [MessageAction(label="{}".format(name), text="{}と取り引きをする".format(name)) for name in names]

        num_last_column_actions = len(actions) % 3
        if num_last_column_actions == 0:
            num_columns = len(actions) // 3
        else:
            num_columns = len(actions) // 3 + 1

        columns = []
        for i in range(num_columns):
            if i == num_columns - 1:
                this_actions = actions[i * 3:]
                while len(this_actions) < 3:
                    this_actions.append(MessageAction(label="無効", text="これは無効です"))
            else:
                this_actions = actions[i * 3 : i * 3 + 3]

            this_column = CarouselColumn(thumbnail_image_url=None,title="【取り引き】だれに持ちかけようか...",text="取り引きをする人を選んでください",actions=this_actions)
            columns.append(this_column)

        line_bot_api.push_message(this_turn_player_class.id, TemplateSendMessage(alt_text="誰と取り引きする？", template=CarouselTemplate(columns=columns)))

    elif take_out_card_name == "一般人":
        line_bot_api.push_message(this_game.id, TextSendMessage(text="何も起きなかった"))
        this_game.this_turn_process = "done"