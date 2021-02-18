from random import shuffle
from get_url import image_urls
import re

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
    def __init__(self):
        self.cards = []
        self.using_cards = []
        for i, info in enumerate(Cards.info):
            for j in range(info[1]):
                self.cards.append(Cards(i))

    def make_using_cards(self, postback_data, num_players):
        num_using_cars = num_players * 4
        if postback_data == "add_card=rand":
            shuffle(self.cards)
            rest_num_card = num_using_cars - len(self.using_cards)
            for i in range(rest_num_card):
                self.using_cards.append(self.cards.pop())

            now_cards = [card.name for card in self.using_cards]
            # for card in self.using_cards:
            #     now_cards.append(card.name)
            reply = "【今回の使用カード】\n" + "\n".join(now_cards)
            return reply
        else:
            add_card_index = int(re.sub("\\D", "", postback_data))
            add_card_name = Cards.info[add_card_index][0]
            pick_up = next((card for card in self.cards if card.name == add_card_name), None)
            try:
                self.cards.remove(pick_up)
                self.using_cards.append(pick_up)
                if len(self.using_cards) < num_using_cars:
                    reply = "{}を追加しました".format(add_card_name)
                else:
                    now_cards = [card.name for card in self.using_cards]
                    # for card in self.using_cards:
                    #     now_cards.append(card.name)
                    reply = "【今回の使用カード】\n" + "\n".join(now_cards)
                return reply
            except:
                reply = "もうありません別のカードを指定してください"
                return reply

class Player:

    def __init__(self, name, user_id, host):
        self.name = name
        self.id = user_id
        self.host = host
        self.hand_cards = []
        self.wins = 0
        self.turn = 0

class Game:

    def __init__(self, players_profile):
        self.players = []
        for player in players_profile:
            self.players.append(Player(player["name"], player["id"], player["host"]))
        self.deck = Deck()
        self.now_turn = 0
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

    def this_turn_info(self):
        """return this_turn_player_class, this_turn"""
        this_turn_player_class = self.players[self.now_turn % len(self.players)]
        this_turn = self.now_turn // len(self.players)
        return this_turn_player_class, this_turn

"""
phase
参加要求：ゲームスタートを押したとき
    ゲームに参加ボタンを送信
    ｜ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    ｜                                             人数選択：パスワード認証後
参加済み：参加者として参加ボタンを押したとき                    ｜
    合言葉要求                                         　　｜
合言葉照合済み：合言葉を送られたとき                           ｜
    全員送られたらホストにカード選択用のカルーセル送信           ｜
    ｜                                             初期カード選択：全員の合言葉照合が完了したとき
    ｜ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
準備：カード選択後
    準備完了ボタンを送信
準備完了：準備完了ボタンを押したら



あなたのターン：ターンになったとき
    カード一覧を送信
    カード選択ボタンを送信

カード選択：選択ボタンを押したとき



"""