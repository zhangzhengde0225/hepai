[![Stars](https://img.shields.io/github/stars/zhangzhengde0225/CDNet)](
https://github.com/zhangzhengde0225/hai)
[![Open issue](https://img.shields.io/github/issues/zhangzhengde0225/CDNet)](
https://github.com/zhangzhengde0225/hai/issues)
<!-- [![Datasets](https://img.shields.io/static/v1?label=Download&message=datasets&color=green)](
https://github.com/zhangzhengde0225/CDNet/blob/master/docs/DATASETS.md)
[![Datasets](https://img.shields.io/static/v1?label=Download&message=source_code&color=orange)](
https://github.com/zhangzhengde0225/CDNet/archive/refs/heads/master.zip) -->

#### 简体中文 | [English](https://github.com/zhangzhengde0225/hai/blob/main/docs/readme_en.md)

# 高能AI框架HepAI
HepAI是一个AI开源框架，是高能AI平台的核心技术，应用此技术可以加速多学科场景的科学研究，简化模型迭代和流程，是开发AI算法和应用的共性基础。

HepAI平台本身是一个软件系统，承载AI算法模型，提供AI计算能力，打通数据通道，并开展AI培训。

HepAI框架集成了高能物理领域的经典和最先进（SOTA）的人工智能算法。用户可以通过统一接口访问相关的算法模型、数据集和计算资源，使AI的应用变得简单高效。

<details open>
<summary><b>News</b></summary>

+ [2024.12.22] v1.1.16 支持远程模型！[点此查看详情](https://aiapi001.ihep.ac.cn/mkdocs/workers/)
+ [2024.05.16] v1.1.9 HepAI Client支持GPT-4o系列模型。
+ [2024.03.26] v1.0.21 Make LLM request like OpenAI via HepAI object.
+ [2023.10.24] v1.0.18 接入dalle文生图模型，调用方法教程见[此处](https://note.ihep.ac.cn/s/EG60U1Rtf)。
+ [2023.04.21] v1.0.7通过hepai使用GPT-3.5，[hepai_api.md](docs/hepai_api.md).
+ [2023.02.09] 基于ChatGPT的**HaiChatGPT**已上线，使用简单，无需梯子！详情查看：[HaiChatGPT](https://code.ihep.ac.cn/zdzhang/haichatgpt).
+ [2023.01.16] 支持华为NPU服务器，如有算法国产化需求，请查阅[NPU文档](docs/computing_power/npu_power_doc.md)。
+ [2022.10.20] HAI v1.0.6-Beta 第一个测试版本发布，4个算法和3个数据集
+ [2022.08.23] HAI v1.0.0
</details>

<details open>
<summary><b>教程</b></summary>

[使用远程模型实现分布式模型、工具及智能体组件](https://aiapi001.ihep.ac.cn/mkdocs/workers/)
[60+深度学习论文代码的实现和解释 ](https://ai.ihep.ac.cn/tutorial/code/)
[在HPC计算集群中使用HepAI的快速入门](docs/quickstart_hpc.md)
[使用PointNet在JUNO实验中重建和识别大气中微子](https://code.ihep.ac.cn/zhangyiyu/pointnet)

</details>

<details open>
<summary><b>模型Zoo</b></summary>
<a href="https://code.ihep.ac.cn/zdzhang/hai/-/blob/main/docs/model_zoo.md">
    <ul>
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=粒子物理&message=4 online, 3 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=天体物理&message=1 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=同步辐射&message=2 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=中子科学&message=1 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=通用神经网络&message=2 online, 5 TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=经典机器学习&message=2 TODO">
    </ul>
    </a>
    
</details>

<details open>
<summary><b>数据集Zoo</b></summary>
<a href="https://code.ihep.ac.cn/zdzhang/hai/-/blob/main/docs/datasets.md">
<ul>
<li>
    <img src="https://img.shields.io/static/v1?style=social&label=粒子物理&message=3 available, 10+ TODO">
    <li>
    <img src="https://img.shields.io/static/v1?style=social&label=CV&message=1 available">
    </a>
</details>


### 快速开始
```
pip install hepai --upgrade
hai -V  # 查看版本
```

1. 命令行使用

    ```bash
    hai train <model_name>  # 训练模型, 例如: hai train particle_transformer
    hai eval <model_name>
    ```

2. python库使用

    python库统一接口：
    ```python
    import hepai as hai
    
    model = hai.hub.load('<model_name>')  # 加载模型
    config = model.config  # 获取模型配置
    config.batch_size = 32  # 修改配置
    model.trian()  # 训练模型
    model.eval()  # 评估模型
    model.infer('<data>')  # 模型推理
    hai.train('particle_transformer')
    ```

3. 部署和远程调用

    跨语言、跨平台的模型部署和远程调用

    服务端：
    ```bash
    hai start server  # 启动服务
    ```
    客户端
    ```python
    from hepai import HepAI
    
    client = HepAI()
    models = client.list_models()
    response = client.chat.completion.create(model="hepai/xiwu_v2", prompt="你好", max_tokens=100)
    print(response.choices[0].text)
    ```