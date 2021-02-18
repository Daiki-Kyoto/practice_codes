from flask import Flask, request, abort
import os
import pickle
import re
import glob
import logging
import random
import string
from random import randint

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage,ButtonsTemplate,URIAction,
    responses, MemberIds, CarouselColumn, CarouselTemplate, MessageAction,ImageCarouselColumn, ImageCarouselTemplate
)
from choice_cards import (
    cards_carousel, cards_explain, game_set, Cards, Deck, Player, Game,
    send_card, first_open_cards, decide_send_card,
    remove_card_form_player, remove_card_name_from_player, card_action, add_card_name_to_player,
    finish_game, save_data, read_data
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

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        if event.message.text == "犯人よ踊れ":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ゲームをするグループでパスワードを入力してください。\npass: "))
            randlst = [random.choice(string.ascii_letters + string.digits) for i in range(10)]
            password = "".join(randlst)
            line_bot_api.push_message(owner_id, TextSendMessage(text="pass:"+password))
            with open("password.binaryfile", "wb") as f:
                pickle.dump(password, f)

        elif "pass:" in event.message.text:
            with open("password.binaryfile", "rb") as f:
                password = pickle.load(f)
            if password in event.message.text:
                actions01 = [MessageAction(label="{}人".format(i), text="「{}人」を選択".format(i)) for i in range(3,6)]
                actions02 = [MessageAction(label="{}人".format(i), text="「{}人」を選択".format(i)) for i in range(6,9)]
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text="犯人よ踊れ",
                        template=CarouselTemplate(
                            columns=[
                                CarouselColumn(thumbnail_image_url=None,title='【犯人は踊る】ゲーム開始',text='人数を選択',actions=actions01),
                                CarouselColumn(thumbnail_image_url=None,title='【犯人は踊る】ゲーム開始',text='人数を選択',actions=actions02)
                            ]
                        )
                    )
                )
            else:
                user_id = event.source.sender_id
                try:
                    with open("wrongpassword.binaryfile","ab") as f:
                        pickle.dump(user_id, f)
                except:
                    with open("wrongpassword.binaryfile","wb") as f:
                        pickle.dump(user_id, f)
                with open("wrongpassword.binaryfile","rb") as f:
                    wrong_user_list = pickle.load(f)
                num = wrong_user_list.count(user_id)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="パスワードが違います。上限を超えて間違えると管理者へ報告されます。"))
                if num > 2:
                    line_bot_api.push_message(owner_id, TextSendMessage(text="{}が不正に入ろうとしました".format(user_id)))

        elif "人」を選択" in event.message.text:
            group_id = event.source.sender_id
            with open("group_id{}.binaryfile".format(group_id), "wb") as f:
                pickle.dump(group_id, f)
            people = re.sub("\\D", "", event.message.text)
            with open("people{}.binaryfile".format(group_id), "wb") as f:
                pickle.dump(people, f)

            players = []
            with open("players{}.binaryfile".format(group_id), "wb") as f:
                pickle.dump(players, f)

            how_to_join = TextSendMessage(text="{}人 の参加者を受付けます\n参加するには私との個人チャットで以下の参加証をコピーして送信してください。".format(people))
            group_id_join = TextSendMessage(text="参加@{}".format(group_id))
            line_bot_api.reply_message(event.reply_token, [how_to_join, group_id_join])

        elif "参加@" in event.message.text:  # 個人チャット
            group_id = event.message.text.split("@")[1]
            user_id = event.source.sender_id
            display_name = line_bot_api.get_profile(user_id).display_name
            try:
                with open("people{}.binaryfile".format(group_id), "rb") as f:
                    people = int(pickle.load(f))
                with open("players{}.binaryfile".format(group_id), "rb") as f:
                    players = pickle.load(f)
                profile = {"user_id": user_id, "display_name": display_name}
                players.append(profile)
                with open("players{}.binaryfile".format(group_id), "wb") as f:
                    pickle.dump(players, f)
                if len(players) < people:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="{}さんの参加が完了しました。\n他の参加者を待っています".format(display_name)))
                elif len(players) == people:
                    players_name = []
                    for i, name in enumerate(players):
                        players_name.append(name["display_name"])
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="{}さんの参加が完了しました。\n参加者が集まりました".format(display_name)))
                    line_bot_api.push_message(group_id, TextSendMessage(text="参加者が全員集まりました\n" + "\n".join(players_name) + "\n次にゲームで使うカードを指定してください。"))
                    cards_carousel(group_id)
                    this_game = game_set(group_id)
                    with open("game{}.binaryfile".format(group_id), "wb") as f:
                        pickle.dump(this_game, f)
            except:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="一致する参加証がありませんでした"))

        elif event.message.text == "今のゲームデッキを教えて":
            group_id = event.source.sender_id
            with open("game{}.binaryfile".format(group_id), "rb") as f:
                this_game = pickle.load(f)
            if len(this_game.deck.using_cards) <= 0:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="まだ何もないよ"))
            else:
                now_cards = []
                for card in this_game.deck.using_cards:
                    now_cards.append(card.name)
                replay = "【現在のカード】\n" + "\n".join(now_cards)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replay))

        elif event.message.text == "カードの説明が欲しいな":
            group_id = event.source.sender_id
            explain = cards_explain()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=explain))
            cards_carousel(group_id)

        elif event.message.text == "「おまかせ」を選択" or "デッキに追加" in event.message.text:
            group_id = event.source.sender_id
            with open("people{}.binaryfile".format(group_id), "rb") as f:
                people = int(pickle.load(f))
            with open("game{}.binaryfile".format(group_id), "rb") as f:
                this_game = pickle.load(f)
            replay = this_game.deck.make_using_cards(event.message.text, people)
            with open("game{}.binaryfile".format(group_id),"wb") as f:
                pickle.dump(this_game, f)


            if len(this_game.deck.using_cards) == people * 4:
                line_bot_api.push_message(group_id, TextSendMessage(text="カードが揃ったので次に進みます。"))
                now_cards = []
                for card in this_game.deck.using_cards:
                    now_cards.append(card.name)
                replay = "【今回の使用カード】\n" + "\n".join(now_cards)
                line_bot_api.push_message(group_id, TextSendMessage(text=replay))
                line_bot_api.push_message(group_id, TemplateSendMessage(alt_text="Game Start", template=ButtonsTemplate(
                    thumbnail_image_url=image_urls[0][0],
                    title="【犯人は踊る】",
                    text="犯人が踊る準備ができたようです。さあ、開始しよう！",
                    actions=[MessageAction(label="開始", text="始めたいから早く配って")]
                )))



        elif event.message.text == "始めたいから早く配って":
            group_id = event.source.sender_id
            with open("game{}.binaryfile".format(group_id), "rb") as f:
                this_game = pickle.load(f)
            if this_game.make_hand_cards == False:
                this_game.make_hand_cards = True
                this_game.make_hands()
                first_open_cards(this_game)
                this_game.players = sorted(this_game.players, key=lambda t:t.turn)
                result = [player.name for player in this_game.players]
                reaction = ["まあ待て", "人生急ぐな", "おいちょ待てよ"]
                rand_message = reaction[randint(0,len(reaction)-1)]
                line_bot_api.reply_message(event.reply_token, [
                    TextSendMessage(text=rand_message),
                    TextSendMessage(text="カードを配ったから確認してみてね"),
                    TextSendMessage(text="ゲームの順番\n" + "→".join(result))
                ])
                line_bot_api.push_message(this_game.players[0].id, TemplateSendMessage(alt_text="カードを出す", template=ButtonsTemplate(title="ゲームを進める", text="カードを出す前にこのボタンを押してください。", actions=[MessageAction(label="カードを選択する", text="カードを出す！")])))
                with open("game{}.binaryfile".format(group_id), "wb") as f:
                    pickle.dump(this_game, f)
                with open("game{}.binaryfile".format(this_game.players[0].id), "wb") as f:
                    pickle.dump(this_game, f)
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="すでに選択されています。"))

        elif event.message.text == "カードを出す！": # 個人チャット
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            this_lap = this_game.now_turn // len(this_game.players)
            this_turn_player = this_game.now_turn % len(this_game.players)
            if event.source.sender_id == this_game.players[this_turn_player].id:
                decide_send_card(this_game.players[this_turn_player], this_lap, event)
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="あなたのターンではありません"))

        elif "」を場に出す" in event.message.text: # 個人チャット
            this_game = read_data(event)
            user_id = event.source.sender_id
            this_lap = this_game.now_turn // len(this_game.players)
            message_lap = int(event.message.text.split("\n")[0][0:-4]) - 1

            this_turn_player = this_game.now_turn % len(this_game.players)
            this_turn_player_class = this_game.players[this_turn_player]

            if event.source.sender_id == this_turn_player_class.id and this_lap == message_lap:
                this_game.now_turn += 1
                take_out_card_name = event.message.text.split("\n")[1][1:-6]
                card = remove_card_name_from_player(take_out_card_name, this_turn_player_class)
                line_bot_api.push_message(this_game.id, TemplateSendMessage(alt_text="出したカード",template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=card.url,action=MessageAction(label=card.name, text=card.explain))])))
                # 各カードのアクション
                card_action(take_out_card_name, this_game, this_turn_player_class)
                if take_out_card_name == "犯人":
                    pass
                else:
                    line_bot_api.push_message(this_game.id, TemplateSendMessage(
                        alt_text="次のターンへ",
                        template=ButtonsTemplate(
                            text="次のターンへ進むときにこちらを押してください",
                            title="{}ターン目{}".format(str(this_lap + 1), this_turn_player_class.name),
                            actions=[MessageAction(
                                label="次へ進む",
                                text="{}ターン目「{}」の番は終わったから次のターンに進めて".format(this_lap + 1, this_turn_player_class.name))
                            ])))

                    with open("game{}.binaryfile".format(this_game.id), "wb") as f:
                        pickle.dump(this_game, f)
                    for player in this_game.players:
                        with open("game{}.binaryfile".format(player.id), "wb") as f:
                            pickle.dump(this_game, f)
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="あなたのターンではありません"))

        elif "」の番は終わったから次のターンに進めて" in event.message.text:
            group_id = event.source.sender_id
            with open("game{}.binaryfile".format(group_id), "rb") as f:
                this_game = pickle.load(f)

            if this_game.this_turn_process == "done":
                this_game.this_turn_process = "not_yet"
                this_game.this_turn_process_all = []
                this_game.this_turn_process_players = len(this_game.players)

                message_lap = int(event.message.text.split("「")[0][0:-4]) - 1
                message_name = event.message.text.split("「")[1][0:-19]
                message_name_player_index = int([player.turn for player in this_game.players if player.name == message_name][0])
                message_turn = message_lap * len(this_game.players) + message_name_player_index

                if message_turn + 1 == this_game.now_turn:
                    this_turn_player_class = this_game.players[this_game.now_turn % len(this_game.players)]
                    try:
                        send_card(this_turn_player_class)
                        line_bot_api.push_message(this_turn_player_class.id, TemplateSendMessage(alt_text="カードを出す", template=ButtonsTemplate(title="ゲームを進める", text="カードを出す前にこのボタンを押してください。", actions=[MessageAction(label="カードを選択する", text="カードを出す！")])))
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="{}の番です。個人トークから次に出すカードを考えてください。".format(this_turn_player_class.name)))
                    except:
                        this_game.this_turn_process = "done"
                        this_game.now_turn += 1
                        this_lap = this_game.now_turn // len(this_game.players)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="{}さんのカードがなくなったので順番を飛ばします。".format(this_turn_player_class.name)))
                        line_bot_api.push_message(this_game.id, TemplateSendMessage(
                            alt_text="次のターンへ",
                            template=ButtonsTemplate(
                                text="次のターンへ進むときにこちらを押してください",
                                title="{}ターン目{}".format(str(this_lap + 1), this_turn_player_class.name),
                                actions=[MessageAction(
                                    label="次へ進む",
                                    text="{}ターン目「{}」の番は終わったから次のターンに進めて".format(this_lap + 1, this_turn_player_class.name))
                                ])))
                    with open("game{}.binaryfile".format(group_id), "wb") as f:
                        pickle.dump(this_game, f)
                    for player in this_game.players:
                        with open("game{}.binaryfile".format(player.id), "wb") as f:
                            pickle.dump(this_game, f)
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="このコマンドは無効です"))
            elif this_game.this_turn_process == "not_yet":
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="まだこのターンは終わっていません。"))

        elif "を疑う" in event.message.text: # 個人チャット
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            group_id = this_game.id
            suspected_player_name = event.message.text[0:-3]
            suspected_player_class = [player for player in this_game.players if player.name == suspected_player_name][0]
            line_bot_api.push_message(group_id, TextSendMessage(text="{}が疑われています。{}は個人トークからアクションしてください".format(suspected_player_name, suspected_player_name)))
            if len(suspected_player_class.hand_cards) == 0:
                line_bot_api.push_message(group_id, TextSendMessage(text="カードがありませんでした。この人は無実です！"))
                this_game.this_turn_process = "done"
            else:
                line_bot_api.push_message(suspected_player_class.id, TemplateSendMessage(alt_text="指示", template=ButtonsTemplate(text="「犯人」または「アリバイ」カードのみ出してください。ない場合は「犯人ではありません」を選択", title="疑いの目", actions=[MessageAction(label="犯人ではありません", text="犯人ではありません")])))
                columns = []
                for card in suspected_player_class.hand_cards:
                    if card.name == "犯人":
                        columns.append(ImageCarouselColumn(image_url=card.url,action=MessageAction(label=card.name, text="白状します。私が犯人です。")))
                    elif card.name == "アリバイ":
                        columns.append(ImageCarouselColumn(image_url=card.url,action=MessageAction(label=card.name, text="犯人ではありません。私にはアリバイがあります。")))
                    else:
                        columns.append(ImageCarouselColumn(image_url=card.url,action=MessageAction(label=card.name, text="他の選択肢を選んでください。これは無効です。")))
                line_bot_api.push_message(suspected_player_class.id, TemplateSendMessage(alt_text="手札",template=ImageCarouselTemplate(columns=columns)))
            with open("game{}.binaryfile".format(group_id), "wb") as f:
                pickle.dump(this_game, f)
            for player in this_game.players:
                with open("game{}.binaryfile".format(player.id), "wb") as f:
                    pickle.dump(this_game, f)

        elif event.message.text == "白状します。私が犯人です。" or event.message.text == "犯人ではありません。私にはアリバイがあります。":
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)

            suspected_player_class = [player for player in this_game.players if player.id == user_id][0]
            if event.message.text == "白状します。私が犯人です。":
                line_bot_api.push_message(this_game.id, TemplateSendMessage(alt_text="犯人", template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=Cards.info[1][3],action=MessageAction(label="犯人",text="{}は犯人です".format(suspected_player_class.name)))])))
                line_bot_api.push_message(this_game.id, TextSendMessage(text="見事探偵は犯人を見つけたようです。{}が白状しました。犯人は{}だったようです。\n{}「{}」".format(suspected_player_class.name, suspected_player_class.name, suspected_player_class.name, event.message.text)))
                finish_game(this_game)
            else:
                line_bot_api.push_message(this_game.id, TemplateSendMessage(alt_text="アリバイ", template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=Cards.info[3][3],action=MessageAction(label="アリバイ",text="{}はアリバイがあります".format(suspected_player_class.name)))])))
                remove_card_name_from_player("アリバイ",suspected_player_class)
                line_bot_api.push_message(this_game.id, TextSendMessage(text="{}は犯人ではなかったようです。{}にはアリバイがありました。どんなアリバイでしたか？".format(suspected_player_class.name, suspected_player_class.name)))
                this_game.this_turn_process = "done"

            save_data(this_game)

        elif event.message.text == "犯人ではありません":
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            player_class = [player for player in this_game.players if player.id == user_id][0]
            line_bot_api.push_message(this_game.id, TextSendMessage(text="{}は犯人ではなかったようです。".format(player_class.name)))
            this_game.this_turn_process = "done"
            save_data(this_game)

        elif "に渡します" in event.message.text: # 個人チャット
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            giver = [player for player in this_game.players if player.id == user_id][0]
            given = [player for player in this_game.players if player.name == event.message.text.split("」")[1][2:]][0]
            given_card_name = event.message.text.split("」")[0][1:]
            remove_card_name_from_player(given_card_name, giver)
            add_card_name_to_player(given_card_name, given)
            line_bot_api.push_message(given.id, TemplateSendMessage(alt_text="手札をみる", template=ButtonsTemplate(text="{}から{}を渡されました。\n手札の結果をみるにはタップしてください".format(giver.name, given_card_name), title="手札交換結果",actions=[MessageAction(label="手札をみる", text="手札を見せて")])))
            this_game.this_turn_process_all.append("done")
            if len(this_game.this_turn_process_all) == this_game.this_turn_process_players:
                this_game.this_turn_process = "done"

            save_data(this_game)

        elif "からもらいました" in event.message.text:
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            taker = [player for player in this_game.players if player.id == user_id][0]
            taken = [player for player in this_game.players if player.name == event.message.text.split("」")[1][2:]][0]
            taken_card_name = event.message.text.split("」")[0][1:]
            remove_card_name_from_player(taken_card_name, taken)
            add_card_name_to_player(taken_card_name, taker)
            line_bot_api.push_message(user_id, TemplateSendMessage(alt_text="手札をみる", template=ButtonsTemplate(text="{}から{}をもらいました。\n手札の結果をみるにはタップしてください".format(taken.name, taken_card_name), title="手札交換結果",actions=[MessageAction(label="手札をみる", text="手札を見せて")])))
            this_game.this_turn_process_all.append("done")
            if len(this_game.this_turn_process_all) == this_game.this_turn_process_players:
                this_game.this_turn_process = "done"

            save_data(this_game)

        elif event.message.text == "手札を見せて":
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            player = [player for player in this_game.players if player.id == user_id][0]
            send_card(player)


        elif "のカードをみる" in event.message.text:
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            witness = [player for player in this_game.players if player.id == user_id][0]
            target_player_name = event.message.text[:-7]
            target_player_class = [player for player in this_game.players if player.name == target_player_name][0]
            columns = []
            for card in target_player_class.hand_cards:
                columns.append(ImageCarouselColumn(image_url=card.url,action=MessageAction(label=card.name, text=card.explain)))
            line_bot_api.push_message(user_id, TemplateSendMessage(alt_text="手札",template=ImageCarouselTemplate(columns=columns)))
            line_bot_api.push_message(this_game.id, TextSendMessage(text="{}は{}のカードを全て見てしまったようだ".format(witness.name, target_player_name)))
            this_game.this_turn_process = "done"
            save_data(this_game)

        elif "から怪しい匂いがする" in event.message.text:
            hide_url = image_urls[0][1]
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            suspected_player_name = event.message.text[:-10]
            suspected_player_class = [player for player in this_game.players if player.name == suspected_player_name][0]
            line_bot_api.push_message(user_id, TextSendMessage(text="以下の{}のカードから最も怪しい匂いのするカードを選んでください".format(suspected_player_name)))
            columns = []
            for card in suspected_player_class.hand_cards:
                if card.name == "犯人":
                    columns.append(ImageCarouselColumn(image_url=hide_url,action=MessageAction(label="？？？", text="見事犯人を当てました。犯人は{}だったようです。".format(suspected_player_name))))
                else:
                    columns.append(ImageCarouselColumn(image_url=hide_url,action=MessageAction(label="？？？", text="違ったようです。{}から怪しい匂いがしたのは{}のカードでした".format(suspected_player_name, card.name))))
            line_bot_api.push_message(user_id, TemplateSendMessage(alt_text="怪しい人の手札（裏）",template=ImageCarouselTemplate(columns=columns)))

        elif "見事犯人を当てました" in event.message.text:
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            player = [player for player in this_game.players if player.id == user_id][0]
            line_bot_api.push_message(this_game.id, TextSendMessage(text="{}は".format(player.name) + event.message.text + "\n{}の勝利です！おめでとうございます！！".format(player.name)))
            finish_game(this_game)

        elif "違ったようです。" in event.message.text:
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            line_bot_api.push_message(this_game.id, TextSendMessage(text=event.message.text))
            this_game.this_turn_process = "done"
            save_data(this_game)

        elif "と取り引きをする" in event.message.text:
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            trader_name = event.message.text[:-8]
            trader = [player for player in this_game.players if player.name == trader_name][0]
            player = [player for player in this_game.players if player.id == user_id][0]
            line_bot_api.push_message(this_game.id, TextSendMessage(text="{}は{}と取り引きをした".format(player.name, trader_name)))
            traders = [trader, player]
            for i, exchanger in enumerate(traders):
                line_bot_api.push_message(exchanger.id, TextSendMessage(text="以下のカードから取り引き相手、{}に渡すカードを選んでください".format(traders[(i + 1) % 2].name)))
                columns = []
                for card in exchanger.hand_cards:
                    columns.append(ImageCarouselColumn(image_url=card.url_red,action=MessageAction(label=card.name, text="「{}」で「{}」と取り引きします".format(card.name, traders[(i + 1) % 2].name))))
                line_bot_api.push_message(exchanger.id, TemplateSendMessage(alt_text="手札",template=ImageCarouselTemplate(columns=columns)))

        elif "と取り引きします" in event.message.text:
            user_id = event.source.sender_id
            with open("game{}.binaryfile".format(user_id), "rb") as f:
                this_game = pickle.load(f)
            player = [player for player in this_game.players if player.id == user_id][0]
            trader = [player for player in this_game.players if player.name == event.message.text.split("」")[1][2:]][0]
            card_name = event.message.text.split("」")[0][1:]
            remove_card_name_from_player(card_name, player)
            add_card_name_to_player(card_name, trader)
            line_bot_api.push_message(trader.id, TemplateSendMessage(alt_text="手札をみる", template=ButtonsTemplate(text="{}からカードをもらいました。\n手札の結果をみるには渡すカードを選んでからタップしてください".format(player.name), title="手札交換結果",actions=[MessageAction(label="手札をみる", text="手札を見せて")])))

            this_game.this_turn_process_all.append("done")
            if len(this_game.this_turn_process_all) == 2:
                this_game.this_turn_process = "done"
            save_data(this_game)

        elif "ゲームを終了" in event.message.text or "ゲームを初期化" in event.message.text:
            group_id = event.source.sender_id
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ゲームを終了し、ゲームデータを初期化します"))
            with open("game{}.binaryfile".format(group_id), "rb") as f:
                this_game = pickle.load(f)
            finish_game(this_game)

        elif "ファイルを表示" in event.message.text:
            filename = glob.glob("*")
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="\n".join(filename)))

        else:
            pass

    except Exception as e:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=str(e)))




if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)



