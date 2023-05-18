"""
Worker类别，具备基本和示例功能
"""

import time
import json
import time
from typing import List, Union
import threading
import uuid
import traceback
import argparse
# import dataclasses
from dataclasses import dataclass, field
import os, sys
from pathlib import Path

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
import requests
import uvicorn

import damei as dm 
here = Path(__file__).parent

try:
    from hai.uaii.worker.utils import auto_port, auto_worker_address, pretty_print_semaphore
    from hai.uaii.worker.base_worker_model import BaseWorkerModel
except:
    sys.path.append(str(here.parent.parent.parent))
    from hai.uaii.worker.utils import auto_port, auto_worker_address, pretty_print_semaphore
    from hai.uaii.worker.base_worker_model import BaseWorkerModel


GB = 1 << 30

logger = dm.get_logger('base_worker.py')
global_counter = 0
model_semaphore = None
WORKER_HEART_BEAT_INTERVAL = 30


def heart_beat_worker(controller):
    while True:
        time.sleep(WORKER_HEART_BEAT_INTERVAL)
        controller.send_heart_beat()

class Worker:
    """
    Worker class, with basic and example functions
    """
    def __init__(self, 
                 controller_addr: str,  # controller的地址
                 worker_addr: str,  # 本worker的地址
                 worker_id: str = None,  # worker的uuid
                 model=None,  # 模型
                 limit_model_concurrency: int = 5,  # 模型并发数
                 stream_interval: int = 2,  # stream的间隔
                 no_register: bool = False,  # 是否注册到controller
                 premissions: any = None,  # 权限
                 **kwargs
                 ):
        
        self.controller_addr = controller_addr
        self.worker_addr = worker_addr
        self.worker_id = worker_id if worker_id else str(uuid.uuid4())[:6]
        self.limit_model_concurrency = limit_model_concurrency
        self.stream_interval = stream_interval
        self.no_register = no_register
        self._premissions = self._init_premissions(premissions)

        self._model = model or BaseWorkerModel()

        if not no_register:
            self.register_to_controller()
            self.heart_beat_thread = threading.Thread(
                target=heart_beat_worker, args=(self,))
            self.heart_beat_thread.start()

    def _init_premissions(self, premissions):
        """worker授予用户或者组的权限"""
        prems = dict()
        if premissions is None:
            pass
        elif isinstance(premissions, str):
            """user: <user1>; user: <user2>; group: <group1>, ..."""
            for a in premissions.split(';'):
                user_or_group, name = a.split(':')
                user_or_group = user_or_group.strip()
                name = name.strip()
                assert user_or_group in ['user', 'group']
                prems[user_or_group] = name
        elif isinstance(premissions, dict):
            prems = premissions
        else:
            raise ValueError(f"premissions should be str or dict, but got {type(premissions)}")
        return prems

    def check_model(self):
        # 测试是否有inference函数
        assert hasattr(self.model, 'inference'), f"Model {self.model_name} has no inference function"

    @property
    def premissions(self):
        return self._premissions
    
    @property
    def model_name(self):
        if self.model is None:
            return None
        return self.model.name

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model    
    
    def register_to_controller(self):
        logger.info(f'Register model "{self.model_name}" to controller.')
        url = self.controller_addr + "/register_worker"
        data = {
            "worker_name": self.worker_addr,
            "check_heart_beat": True,
            "worker_status": self.get_status(),
            }
        r = requests.post(url, json=data)
        assert r.status_code == 200

    def send_heart_beat(self):
        logger.info(f"Send heart beat. Models: {[self.model_name]}. "
                    f"Semaphore: {pretty_print_semaphore(model_semaphore)}. "
                    f"global_counter: {global_counter}")

        url = self.controller_addr + "/receive_heart_beat"

        while True:
            try:
                ret = requests.post(url, json={
                    "worker_name": self.worker_addr,
                    "queue_length": self.get_queue_length()}, timeout=5)
                exist = ret.json()["exist"]
                break
            except requests.exceptions.RequestException as e:
                logger.error(f"heart beat error: {e}")
            time.sleep(5)

        if not exist:
            self.register_to_controller()

    def get_queue_length(self):
        if model_semaphore is None:
            return 0
        else:
            _value = model_semaphore._value
            _num_waiters = len(model_semaphore._waiters) if model_semaphore._waiters is not None else 0
            return self.limit_model_concurrency - _value + _num_waiters

    def get_status(self):
        try:
            misc = self.model.get_misc()
        except:
            misc = None
        return {
            "model_names": [self.model_name],
            "speed": 1,
            "queue_length": self.get_queue_length(),
            "premissions": self.premissions,
            "misc": misc,
        }

    def _sleep(self, seconds):
        if float(seconds) == 0. or seconds is None:
            return
        if seconds < 0:
            raise ValueError(f"stream_interval should be positive, but got {seconds}")
        if seconds > 3:
            raise ValueError(f"stream_interval should be less than 3, but got {seconds}")
        time.sleep(seconds)

    
    def get_generator_content_and_verify_one(self, generator):
        """
        从生成器中获取内容，并验证是否只有一个元素
        """
        try:
            content = next(generator)
            print('content: ', content)
        except StopIteration as e:
            print(f'Generator is empty: {e} {type(e)}')
            return e
            # raise ValueError(f"Generator is empty: {e} {type(e)}")
        try:
            next(generator)
            raise ValueError("Generator should only have one element")
        except StopIteration:
            pass
        return content

    
    def generate_stream_gate(self, **params):
        """
        生成流式响应的门
        :param params:
                model: 模型名
                其他参数
        :return:
        """
        
        stream = params.get("stream", False)
        stream_interval = params.get("stream_interval", self.stream_interval)

        def yield_data(output):
            if isinstance(output, int):
                output = str(output)
                yield output.encode() + b"\0"
            elif isinstance(output, str):
                for x in output:
                    yield x.encode() + b"\0"
            elif isinstance(output, bytes):
                yield output + b"\0"
            elif isinstance(output, list):
                output = str(output)
                yield output.encode() + b"\0"
            elif isinstance(output, dict):
                yield json.dumps(output).encode() + b"\0"
            else:
                raise ValueError(f'output type {type(output)} not supported')

        try:
            output = self.model.inference(**params)
            if not stream:
                # print(f'output: {output}')
                new_output = dict()
                new_output["message"] = output
                new_output["status_code"] = 42901
                yield json.dumps(new_output).encode()
                return
            else:
                if isinstance(output, (int, str, bytes, list, dict)):
                    yield from yield_data(output)
                    self._sleep(stream_interval)
                # 如果是python的generator
                elif hasattr(output, '__next__'):
                    for x in output:
                        yield from yield_data(x)
                        self._sleep(stream_interval)
                else:
                    raise ValueError(f'output type {type(output)} not supported')
                yield "[DONE]".encode() + b"\0"

        except Exception as e:
            error_info = f'{type(e)} {e}'
            logger.error(f'error_info: {error_info}\n {traceback.format_exc()}')
            ret = {
                "message": error_info,
                "status_code": 42904, 
            }
            yield json.dumps(ret).encode() + b"\0"

    def train(self, **kwargs):
        ret = self.model.train(**kwargs)
        return ret


from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio


class WorkerAPP(FastAPI):

    def __init__(self):
        super().__init__()
        self._worker = None

    @property
    def worker(self):
        if self._worker is None:
            raise ValueError(
                f"worker is not initialized, \
                please call `WorkerAPP.worker = BaseWorker(**kwargs)` first")
        return self._worker
    
    @worker.setter
    def worker(self, worker):
        self._worker = worker
        
app = WorkerAPP()  # It's a FastAPI instance


def release_model_semaphore():
    model_semaphore.release()

@app.post("/worker_generate_stream")
async def generate_stream(request: Request):
    global model_semaphore, global_counter
    global_counter += 1
    params = await request.json()

    if model_semaphore is None:
        model_semaphore = asyncio.Semaphore(
            app.worker.limit_model_concurrency)
        # 用于设置模型的并发请求，并发达到该值时，后续请求会被阻塞，直到之前的请求完成释放了锁
    await model_semaphore.acquire()
    generator = app.worker.generate_stream_gate(**params)
    background_tasks = BackgroundTasks()  # 背景任务
    background_tasks.add_task(release_model_semaphore)  # 释放锁
    return StreamingResponse(generator, background=background_tasks)

@app.post("/train")
async def train(request: Request):
    global model_semaphore, global_counter
    global_counter += 1
    params = await request.json()
    if model_semaphore is None:
        model_semaphore = asyncio.Semaphore(
            app.worker.limit_model_concurrency
        )
    await model_semaphore.acquire()
    result = app.worker.train(**params)
    background_tasks = BackgroundTasks()  # 背景任务
    background_tasks.add_task(release_model_semaphore)  # 释放锁
    return result


@app.post("/worker_get_status")
async def get_status(request: Request):
    return app.worker.get_status()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=str, default='auto')
    parser.add_argument("--controller-address", type=str,
        default="http://127.0.0.1:42901")
    parser.add_argument("--worker-address", type=str,
        default="auto")
    parser.add_argument("--limit-model-concurrency", type=int, default=5, help="限制模型的并发请求")
    parser.add_argument("--stream-interval", type=int, default=0., help="额外的流式响应间隔")
    parser.add_argument("--no-register", action="store_true", help="不注册到控制器")
    parser.add_argument("--premissions", type=str, default='group: all', 
        help="模型权限授予谁,写法：'user: <user1>; user: <user2>; group: <group1>, ...'")
    args = parser.parse_args()
    logger.info(f"Args: {args}")
    return args


@dataclass
class BaseWorkerArgs:
    host: str = "0.0.0.0"  # worker的地址，0.0.0.0表示外部可访问，127.0.0.1表示只有本机可访问
    port: str = "auto"  # 默认从42902开始
    controller_address: str = "http://chat.ihep.ac.cn:42901"  # 控制器的地址
    worker_address: str = "auto"  # 默认是http://<ip>:<port>
    limit_model_concurrency: int = 5  # 限制模型的并发请求
    stream_interval: float = 0.  # 额外的流式响应间隔
    no_register: bool = False  # 不注册到控制器
    premissions: str = 'group: all'  # 模型的权限授予，分为用户和组，用;分隔
    
def run_worker(model=None, test=False, daemon=False, **kwargs):
    # args = get_args() if args is None else args
    import transformers
    args = transformers.HfArgumentParser((BaseWorkerArgs,)).parse_args_into_dataclasses()[0]
    args.port = auto_port(args.port, start=42902)
    args.worker_address = auto_worker_address(args.worker_address, args.host, args.port)
    if test:
        args.controller_address = "http://chat.ihep.ac.cn:4444"

    # 更新
    for k, v in kwargs.items():
        if hasattr(args, k):
            setattr(args, k, v)

    logger.info(f'args: {args}')

    worker  = Worker(
        args.controller_address,
        args.worker_address,
        model=model,
        limit_model_concurrency=args.limit_model_concurrency,
        stream_interval=args.stream_interval,
        no_register=args.no_register,
        premissions=args.premissions
        )
    
    app.worker = worker

    logger.info(f"Controller address: {args.controller_address}")
    if daemon:
        print(f"Daemon Worker address: {args.worker_address}")
        import threading
        t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={
            "host": args.host, "port": args.port, "log_level": "info"
            })
        t.setDaemon(True)
        t.start()
    else:
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return args.worker_address


class WorkerWarper:
    @staticmethod
    def start(daemon=False, **kwargs):
        return run_worker(daemon=daemon, **kwargs)


if __name__ == "__main__":
    run_worker(test=False)
    
    





