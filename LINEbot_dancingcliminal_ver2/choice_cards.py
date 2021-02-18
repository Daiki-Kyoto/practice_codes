from random import shuffle
# import numpy as np
import pickle
import glob
import os

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, URIAction,
    responses, MemberIds, CarouselColumn, CarouselTemplate,
    PostbackAction, MessageAction, URIAction, ImageCarouselColumn, ImageCarouselTemplate
)


# ファイルからインポート
from files_manegiment import (
    deel_file
)
from general_setting import (
    Game, Cards
)
from get_url import image_urls

from linebotapi import(
    line_bot_api, send_textmessage
)



def cards_carousel(sender_id):
    """使用カード選択用カルーセル"""
    # kind_cards = np.array(Cards.info)[:, 0]
    kind_cards = ["第一発見者", "犯人", "探偵", "アリバイ", "たくらみ", "情報操作", "うわさ", "目撃者", "少年", "いぬ", "取り引き", "一般人"]
    actions = [PostbackAction(label=kind_cards[i], data="add_card={}".format(i)) for i in range(12)]
    actions.append(PostbackAction(label="おまかせ", data="add_card=rand"))
    actions.append(PostbackAction(label="説明をみる", data="card_explain"))
    actions.append(PostbackAction(label="現在のデッキを確認", data="now_deck"))
    columns = [CarouselColumn(thumbnail_image_url=None, title='カード選択', text='使用するカードを選択\n複数回可', actions=actions[i * 3:(i + 1) * 3]) for i in range(5)]

    line_bot_api.push_message(sender_id,TemplateSendMessage(alt_text="使用するカードを選択",template=CarouselTemplate(columns=columns)))


def cards_explain():
    cards_info = []
    for card in Cards.info:
        cards_info.append(card[0] + " {}枚\n".format(card[1]) + card[2])
    explain = "\n\n".join(cards_info)
    return "【カード一覧】\n" + explain



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
                # save_data(this_game)

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