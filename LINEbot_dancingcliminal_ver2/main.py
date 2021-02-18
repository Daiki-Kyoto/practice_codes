"""This is a test program."""
import os
import random
import string
import re
from flask import Flask, request, abort

# LINE bot sdk
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent, TextMessage,
    PostbackEvent,
    TextSendMessage
)

# linebotapi.py から変数を読み込み
from linebotapi import (
    line_bot_api, handler, OWNER_ID,
    send_textmessage,
    game_start, how_many_player, first_open_cards, send_card
)

from files_manegiment import (
    deel_file, phase_change
)

from choice_cards import (
    cards_carousel
)
from general_setting import (
    Game
)


app = Flask(__name__)

@app.route("/")
def hello_world():
    """テスト用の関数"""
    return "hello world!"

@app.route("/callback", methods=["POST"])
def callback():
    """X-Line-Signatureの照合"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# イベントへのレスポンス #######################################################################
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """メッセージイベント"""
    try:
        reply_token = event.reply_token
        sender_id = event.source.sender_id
        display_name = line_bot_api.get_profile(sender_id).display_name
        message = event.message.text

        if message == "犯人よ踊れ":
            deel_file("phase{}.binaryfile".format(sender_id), "参加要求")
            game_start(reply_token)
        elif message == "手札を見せて":
            pass
        elif message == "カードの説明が欲しい":
            pass
        elif message == "今回の使用カードは？":
            pass
        elif "pass" in message:
            try:
                password = deel_file("password{}.binaryfile".format(sender_id), None, False)
                if password in message:
                    how_many_player(reply_token)
                    send_textmessage(sender_id, ["パスワードを確認しました。\n次に参加人数を選択してください。"], False)
                    phase_change(sender_id, "人数選択")
                else:
                    send_textmessage(reply_token, ["パスワードが違います。"])
            except:
                send_textmessage(reply_token, ["パスワードが違います。"])
        elif message == "準備OK！！":
            phase = deel_file("phase{}.binaryfile".format(sender_id), None, False)
            if phase == "準備":
                phase_change(sender_id, "準備完了")
                this_game = deel_file("game{}.binaryfile".format(sender_id), None, False)
                this_game.this_turn_process_all.append("done")
                for player in this_game.players:
                    deel_file("game{}.binaryfile".format(player.id), this_game)
                    if player.id != sender_id:
                        send_textmessage(player.id, ["[" + player.name + "]:" + message], False)
                if len(this_game.this_turn_process_all) == this_game.this_turn_process_players:
                    # ゲーム開始へ
                    pass
        else:
            try:
                pass_pass = deel_file("password{}.binaryfile".format(sender_id), None, False)
                if pass_pass == True:
                    # passwordを使用済みにする
                    deel_file("password{}.binaryfile".format(sender_id), False)
                    # 合言葉を登録
                    deel_file("secret_word.binaryfile", message)
                    send_textmessage(reply_token, ["正常に合言葉が登録されました。\n合言葉：{}".format(message)])
                    # 人数を取得し合言葉で取得できるようにする
                    num_players = deel_file("num_players{}.binaryfile".format(sender_id), None, False)
                    deel_file("num_players{}.binaryfile".format(message), num_players)
                    # 参加者名格納用リストとホストを参加者に入力
                    players = []
                    profile = {"id": sender_id, "name": display_name, "host": True}
                    players.append(profile)
                    deel_file("players{}.binaryfile".format(message), players)
            except Exception as e:
                try:
                    secret_word = deel_file("secret_word.binaryfile", None, False)
                    phase = deel_file("phase{}.binaryfile".format(sender_id), None, False)
                    if secret_word == message and phase == "参加済み":
                        phase_change(sender_id, "合言葉照合済み")
                        num_players = int(deel_file("num_players{}.binaryfile".format(message), None, False))
                        players = deel_file("players{}.binaryfile".format(message), None, False)
                        if len(players) < num_players:
                            # プロフィールを取得し、プレーヤーに設定、保存
                            profile = {"id": sender_id, "name": display_name, "host": False}
                            players.append(profile)
                            deel_file("players{}.binaryfile".format(message), players)
                            send_textmessage(reply_token, ["合言葉が見つかりました。"])
                            if len(players) == num_players:
                                this_game = Game(players)
                                for player in players:
                                    deel_file("game{}.binaryfile".format(player["id"]), this_game)
                                    if player["host"]:
                                        phase_change(player["id"], "初期カード選択")
                                        send_textmessage(player["id"], ["参加者が揃いました。\n以下から使用するカードを選んでください。"], False)
                                        cards_carousel(player["id"])
                                    else:
                                        send_textmessage(player["id"], ["参加者が揃いました。\nホストが使用するカードを選択しています。下部のメニュー「使用カード一覧」から現在の使用カードがわかります。"])


                except Exception as e2:
                    if message == "エラー表示":
                        send_textmessage(reply_token, [str(e), str(e2)])
    except Exception as e:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(e)))



@handler.add(PostbackEvent)
def handle_postback(event):
    """ポストバックイベント"""
    reply_token = event.reply_token
    sender_id = event.source.sender_id
    postback_data = event.postback.data
    phase = deel_file("phase{}.binaryfile".format(sender_id), None, False)

    if "join" in postback_data and phase == "参加要求":
        if postback_data == "join=participant":
            phase_change(sender_id, "参加済み")
            # 合言葉を要求
            send_message = "参加者として登録されます。ホストが決めた合言葉を入力してください"
            send_textmessage(reply_token, [send_message])

        elif postback_data == "join=host":
            # パスワードを生成
            randlst = [random.choice(string.ascii_letters + string.digits) for i in range(10)]
            password = "".join(randlst)
            deel_file("password{}.binaryfile".format(sender_id), password)
            # 自分に送信
            send_textmessage(OWNER_ID, [password], False)
            # パスワードを要求
            request_pass = "パスワードを入力してください。\npass:"
            send_textmessage(reply_token, [request_pass])


    elif "num_players" in postback_data and phase == "人数選択":
        phase_change(sender_id, False)
        num_players = re.sub("\\D", "", postback_data)
        deel_file("num_players{}.binaryfile".format(sender_id), num_players)
        deel_file("password{}.binaryfile".format(sender_id), True)
        send_textmessage(reply_token, ["参加人数を{}人で設定します。".format(num_players), "合言葉を送信してください。(1度のみ適用)"])

    elif "add_card" in postback_data and phase == "初期カード選択":
        this_game = deel_file("game{}.binaryfile".format(sender_id), None, False)
        reply = this_game.deck.make_using_cards(postback_data, len(this_game.players))
        if "追加しました" in reply:
            for player in this_game.players:
                deel_file("game{}.binaryfile".format(player.id), this_game)
                if player.host:
                    send_textmessage(reply_token, [reply])
                else:
                    send_textmessage(player.id, [reply], False)
        elif "今回の使用カード" in reply:
            first_open_cards(this_game, reply)
            for player in this_game.players:
                deel_file("game{}.binaryfile".format(player.id), this_game)
                # 全員のフェーズを準備に移行
                phase_change(player.id, "準備")
        elif "もうありません" in reply:
            send_textmessage(reply_token, [reply])

    elif postback_data == "":
        pass
    elif postback_data == "":
        pass
    elif postback_data == "":
        pass



if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
