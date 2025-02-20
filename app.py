import streamlit as st
import streamlit_authenticator as stauth
import requests
import json

# ----- Basic認証の設定 -----
credentials = {
    "usernames": {
        "demo": {
            "name": "Demo User",
            "password": "demo",  # 本番ではハッシュ化されたパスワードを利用してください
            "email": "demo@example.com",
        }
    }
}

# Authenticatorオブジェクトの作成
authenticator = stauth.Authenticate(
    credentials,
    "test_cookie",  # クッキー名
    "abcdef",  # クッキー署名キー（十分に長くランダムな文字列を推奨）
    cookie_expiry_days=30,
)

# ログインフォームをメイン画面（location="main"）に表示
authenticator.login(
    location="main", fields={"Form name": "ログイン"}  # フォームのタイトルを日本語化
)

# ここで session_state からログイン状態を確認
authentication_status = st.session_state.get("authentication_status", None)
name = st.session_state.get("name", None)
username = st.session_state.get("username", None)

# ログイン状態に応じて分岐
if authentication_status is True:
    # ログイン成功時
    st.success(f"ようこそ、{name}さん！")

    # ----- ここからチャットボットのUI -----
    st.title("商品レビュー感情分析チャットボット")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_review = st.text_input("商品レビューを入力してください:")

    if st.button("送信"):
        if user_review.strip() == "":
            st.warning("レビューを入力してください。")
        else:
            st.session_state.chat_history.append(
                {"sender": "user", "message": user_review}
            )

            # 正しいAPIエンドポイントを設定（例: /chat-messages）
            api_url = "https://api.dify.ai/v1/chat-messages"

            payload = {
                "query": user_review,
                "inputs": {},
                "response_mode": "blocking",
                "user": "your_unique_user_id",
                "conversation_id": "",
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer app-MtzKCfM4dnpMX0cGFgGMDZDE",
            }

            try:
                response = requests.post(
                    api_url, data=json.dumps(payload), headers=headers
                )
                response.raise_for_status()
                data = response.json()
                bot_message = f"判定: {data.get('answer', '判定結果なし')}"
                st.session_state.chat_history.append(
                    {"sender": "bot", "message": bot_message}
                )
            except Exception as e:
                error_msg = f"エラーが発生しました: {e}"
                st.session_state.chat_history.append(
                    {"sender": "bot", "message": error_msg}
                )

    # チャット履歴の表示
    st.markdown("### チャット履歴")
    for chat in st.session_state.chat_history:
        if chat["sender"] == "user":
            st.markdown(f"**あなた:** {chat['message']}")
        else:
            st.markdown(f"**ボット:** {chat['message']}")

    # ログアウトボタンの表示
    authenticator.logout("ログアウト", "main")

elif authentication_status is False:
    # ログイン失敗時
    st.error("ユーザー名またはパスワードが正しくありません")

else:
    # authentication_status is None の場合（まだログインしていない）
    st.warning("ログインしてください")
