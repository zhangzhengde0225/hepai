
import os, sys
from pathlib import Path
here = Path(__file__).parent

try:
    from hepai import __version__
except:
    sys.path.insert(1, str(here.parent.parent.parent))
    from hepai import __version__

from openai import OpenAI
from hepai import HepAI, ChatCompletion

# proxy = "http://192.168.32.148:8118"
# base_url = "https://api.openai.com/v1"
# api_key = os.getenv("OPENAI_API_KEY")
# model = "gpt-3.5-turbo"

proxy = None
base_url = "http://localhost:42901/v1"
api_key = os.getenv("HEPAI_A100_API_KEY")
model = "lmsys/vicuna-7b"

# client = OpenAI(
client = HepAI(
    api_key=api_key,
    base_url=base_url,
    proxy=proxy,
)

completion: ChatCompletion = client.chat.completions.create(
  model=model,
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "who  are you?"}
  ]
)

print(completion)
print(completion.choices[0].message)