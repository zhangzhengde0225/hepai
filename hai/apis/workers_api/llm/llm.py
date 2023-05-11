

import os
import requests



class HaiLLM(object):

    @staticmethod
    def chat(model, messages=None, **kwargs):
        """Create a LLM instance.

        :param model: The model name.
        :param messages: The messages.
        :return: The LLM instance.
        """
        api_key = kwargs.pop("api_key", os.getcwd('HEPAI_API_KEY', None))

        session = requests.Session()
        host = kwargs.get("host", "chat.ihep.ac.cn")
        port = kwargs.get("port", None)
        if port is not None:
            url = f"http://{host}:{port}/v1/chat/completions"
        else:
            url = f"https://{host}/v1/chat/completions"

        data = dict()
        data['model'] = model
        data['messages'] = messages
        data['stream'] = kwargs.pop('stream', True)
        data.update(kwargs)
        # print(f'data: {data}')

        assert api_key, """
The HepAI API-KEY is required. Please set the environment variable `HEPAI_API_KEY` via `export HEPAI_API_KEY=xxx`.
Alternatively, it can be provided by passing in the `api_key` parameter when calling the `chat` method.
"""
        response = session.post(
            # f"http://{host_and_port}/v1/chat/completions",
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=data,
            stream=True,
            timeout=60,
            )
        # print(f'llm response: {response}')
        full_response = ""
        # print('llm streaming:')
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if not chunk:
                continue
            chunk = chunk.decode('utf-8')
            if chunk == "[DONE]":
                break
            full_response += chunk
            # print(f'\r{full_response}', end='')
            yield chunk

        # print('\n')
        # print(f'full_response: {full_response}')
        # print(model, messages)


if __name__ == '__main__':
    # llm = HaiLLM
    model = 'hepai/chathep-20230509'
    # model = 'hepai/gpt-3.5-turbo'
    api_key = os.getenv('HEPAI_API_KEY')
    messages = [
        {'role': 'system', 'content': 'You are a bot.'},
        {'role': 'user', 'content': 'Hello, how are you?'}
    ]
    # messages = [
    #     {"role": "system", "content": 'Yo'},
    #     {"role": "user", "content": 'Hello'},
    #     ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
    #     ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
    # ]
    ret =  HaiLLM.chat(model, api_key=api_key, messages=messages)
    for x in ret:
        print(x)
    print(ret)
