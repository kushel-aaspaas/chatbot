from flask import Flask, render_template
from flask_socketio import SocketIO
from openai import OpenAI

client = OpenAI(
  api_key='<openai-api-key',
)
app = Flask(__name__)
socketio = SocketIO(app)

conversation_history = [
    ]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):

    def generate_response(model, prompt, conversation_history):
        input_text = ""
        for message in conversation_history:
            input_text += f"{message['role']}: {message['content']} "
        prompt_with_history = f"{input_text}User: {prompt}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_with_history}
            ]
        )

        return response.choices[0].message

    def add_to_conversation_history(conversation_history, user_input, assistant_response):
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": assistant_response})

    model_name = "gpt-3.5-turbo"

    response = generate_response(model_name, msg, conversation_history)
    print("Assistant:", response.content)


    add_to_conversation_history(conversation_history, msg, response)    

    socketio.emit('message', {'user': None, 'assistant': response.content})

if __name__ == '__main__':
    socketio.run(app, debug=True)