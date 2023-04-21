
## 如何通过hepai的API使用GPT-3.5

+ 无需openai账号和梯子
+ turbo模型，速度快
+ 需要hepai的api_key

## 安装hepai
```
pip install hepai --upgrade
```
### 安装依赖包
```
pip install opencv-python
pip install pillow
pip install tqdm
```

## 使用

```python

import hai

models = hai.Model.list()  # 列出可用模型
print(models)

system_prompt = "You are ChatGPT, answering questions conversationally"
prompt = "Hello!"

api_key = 'your api key'

result = hai.LLM.chat(
        model='hepai/gpt-3.5-turbo',
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
            ## 如果有多轮对话，可以继续添加，"role": "assistant", "content": "Hello there! How may I assist you today?"
            ## 如果有多轮对话，可以继续添加，"role": "user", "content": "I want to buy a car."
        ],
        stream=True,
    )
# result是一个流式数据生成器，需要遍历获取全部结果

full_result = ""
for i in result:
    full_result += i
    print(f'\r{full_result}', end='')
print()
```

联系zdzhang@ihep.ac.cn获取hepai的api_key
