import json
import os

import openai
import tkinter as tk
import pandas as pd
from tkinter import scrolledtext
import tkinter.filedialog as filedialog

openai.api_key = os.environ["API_KEY"]


def get_all_data():
    files = ["kakao_social.txt", "kakao_sink.txt", "kakao_channel.txt"]
    data = []
    for file in files:
        with open(f"data/{file}", "r") as fin:
            data.append(fin.read())
    return data


def send_message(message_log, gpt_model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=gpt_model,
        messages=message_log,
        temperature=temperature,
    )
    return response.choices[0].message.content


def main():
    message_log = [
        {
            "role": "system",
            "content": '''
            당신은 친절한 Q&A 봇입니다. Context를 참고해서 사용자의 질문에 답해주세요.
            '''
        }
    ]

    def show_popup_message(window, message):
        popup = tk.Toplevel(window)
        popup.title("")

        # 팝업 창의 내용
        label = tk.Label(popup, text=message, font=("맑은 고딕", 12))
        label.pack(expand=True, fill=tk.BOTH)

        # 팝업 창의 크기 조절하기
        window.update_idletasks()
        popup_width = label.winfo_reqwidth() + 20
        popup_height = label.winfo_reqheight() + 20
        popup.geometry(f"{popup_width}x{popup_height}")

        # 팝업 창의 중앙에 위치하기
        window_x = window.winfo_x()
        window_y = window.winfo_y()
        window_width = window.winfo_width()
        window_height = window.winfo_height()

        popup_x = window_x + window_width // 2 - popup_width // 2
        popup_y = window_y + window_height // 2 - popup_height // 2
        popup.geometry(f"+{popup_x}+{popup_y}")

        popup.transient(window)
        popup.attributes('-topmost', True)

        popup.update()
        return popup

    def on_send():
        context = {"role": "user", "content": f"Context: get_all_data"}
        message_log.append(context)

        user_input = user_entry.get()
        user_entry.delete(0, tk.END)

        if user_input.lower() == "quit":
            window.destroy()
            return

        message_log.append({"role": "user", "content": user_input})
        conversation.config(state=tk.NORMAL)  # 이동
        conversation.insert(tk.END, f"You: {user_input}\n", "user")  # 이동
        thinking_popup = show_popup_message(window, "처리중...")
        window.update_idletasks()
        response = send_message(message_log)
        thinking_popup.destroy()

        message_log.append({"role": "assistant", "content": response})

        conversation.insert(tk.END, f"gpt assistant: {response}\n", "assistant")
        conversation.config(state=tk.DISABLED)
        conversation.see(tk.END)

    window = tk.Tk()
    window.title("GPT AI")

    font = ("맑은 고딕", 10)

    conversation = scrolledtext.ScrolledText(window, wrap=tk.WORD, bg='#f0f0f0', font=font)
    conversation.tag_configure("user", background="black")
    conversation.tag_configure("assistant", background="red")
    conversation.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    input_frame = tk.Frame(window) 
    input_frame.pack(fill=tk.X, padx=10, pady=10)

    user_entry = tk.Entry(input_frame)
    user_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

    send_button = tk.Button(input_frame, text="Send", command=on_send)
    send_button.pack(side=tk.RIGHT)

    window.bind('<Return>', lambda event: on_send())
    window.mainloop()


if __name__ == "__main__":
    main()
