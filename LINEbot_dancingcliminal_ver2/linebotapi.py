"""This is a test program."""
from random import shuffle



from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (
    TextSendMessage, TemplateSendMessage,
    ButtonsTemplate,
    CarouselTemplate, CarouselColumn,
    ImageCarouselTemplate, ImageCarouselColumn,
    MessageAction, PostbackAction
)

from get_url import image_urls
from general_setting import(
    Game
)

YOUR_CHANNEL_ACCESS_TOKEN = "07/xcMMu+QoPR3wcZg4FJW5Kc5tWzfdILXFmHttekLkpjqvbWhw21id0K2O3GohlpAuP84O1LxGz/3EmvCcj1qcVGfbenAwJLJEzrQVXhatnn2tfrNRda/7uQSLwrUD7CaDYvoqLk8D/J911fo9pNgdB04t89/1O/w1cDnyilFU="
YOUR_CHANNEL_SECRET = "088336230fa1d600499669231f6590be"
OWNER_ID = "U4a91bdd11f17b03c08567d9770979fb5"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


def send_textmessage(id_or_token, send_text, reply=True):
    """Default is reply_message"""
    send_texts = [TextSendMessage(text=text) for text in send_text]
    if reply:
        line_bot_api.reply_message(id_or_token, send_texts)
    else:
        line_bot_api.push_message(id_or_token, send_texts)


def game_start(id_or_token):
    """ホストか参加者かを選択"""
    line_bot_api.reply_message(
        id_or_token,
        TemplateSendMessage(
            alt_text="参加形態選択",
            template=ButtonsTemplate(
                text="ホストとして参加する場合はホストを、それ以外は参加者を選択してください。",
                title="ゲームに参加",
                thumbnail_image_url=None,
                actions=[
                    PostbackAction(label="ホスト", data="join=host", text="ホストとして参加します"),
                    PostbackAction(label="参加者", data="join=participant", text="参加者として参加します")
                ]
            )
        )
    )


def how_many_player(reply_token):
    actions01 = [PostbackAction(label="{}人".format(i), data="num_players={}".format(i)) for i in range(2, 5)]
    actions02 = [PostbackAction(label="{}人".format(i), data="num_players={}".format(i)) for i in range(5, 8)]
    line_bot_api.reply_message(
        reply_token,
        TemplateSendMessage(
            alt_text="犯人よ踊れ",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='【犯人は踊る】ゲーム開始',
                        text='人数を選択',
                        actions=actions01
                    ),
                    CarouselColumn(
                        thumbnail_image_url=None,
                        title='【犯人は踊る】ゲーム開始',
                        text='人数を選択',
                        actions=actions02
                    )
                ]
            )
        )
    )

def send_card(player_class, back=False):
    """現在のカードをそのプレーヤーに送信"""
    user_id = player_class.id
    cards = player_class.hand_cards
    shuffle(cards)
    card_back_url = image_urls[0][1]
    columns = []
    if not back:
        for card in cards:
            columns.append(
                ImageCarouselColumn(
                    image_url=card.url,
                    action=MessageAction(label=card.name, text=card.explain)
                )
            )
    else:
        for card in cards:
            columns.append(
                ImageCarouselColumn(
                    image_url=card_back_url,
                    action=MessageAction(label="？？？", text=card.name)
                )
            )
    line_bot_api.push_message(
        user_id,
        TemplateSendMessage(alt_text="手札", template=ImageCarouselTemplate(columns=columns))
    )




def first_open_cards(game, reply):
    """第一発見者はあなたですorあなたの順番は○番目です"""
    # カードの配布
    game.make_hands()
    # ゲームの順番を決定
    turn = [i for i in range(1, len(game.players))]
    shuffle(turn)
    for player in game.players:
        cards = [card.name for card in player.hand_cards]
        if "第一発見者" in cards:
            player.turn = 0
        else:
            player.turn = turn.pop()
    # 出力内容を作成
    game.players = sorted(game.players, key=lambda t: t.turn)
    result = [player.name for player in game.players]
    result = "ゲームの順番\n" + "→".join(result)
    for player in game.players:
        if player.turn == 0:
            your_turn = "第一発見者はあなたです。あなたから事件は始まります。"
        else:
            your_turn = "あなたの順番は{}番目です。".format(player.turn + 1)
        send_textmessage(player.id, [
            "カードが揃いました。ゲームを開始します。",
            reply,
            result,
            your_turn
        ], False)
        send_card(player)

def choice_card_button(this_game):
    this_turn_player_class, this_turn = this_game.this_turn_info()
    line_bot_api.push_message(
        this_turn_player_class.id,
        TemplateSendMessage(
            alt_text="カードを出す",
            template=ButtonsTemplate(
                title="ゲームを進める",
                text="カードを出す前にこのボタンを押してください。",
                actions=[
                    MessageAction(
                        label="カードを選択する",
                        text="カードを出す！"
                    )
                ]
            )
        )
    )







def Are_you_ready(player_class):
    line_bot_api.push_message(player_class.id, TemplateSendMessage(alt_text="Game Start", template=ButtonsTemplate(
        thumbnail_image_url=image_urls[0][0],
        title="【犯人は踊る】",
        text="犯人が踊る準備ができたようです。さあ、開始しよう！\n準備ができたら開始を押してね！",
        actions=[PostbackAction(label="開始", data="i_am_ready", text="準備OK！！")]
    )))


def your_turn():
