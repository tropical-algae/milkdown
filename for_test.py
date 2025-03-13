from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionUserMessageParam
import ast



client = OpenAI(
    base_url="https://api.chatanywhere.tech/v1",
    api_key="sk-py9OkjZho3MDtoBuq4H9y9mXHhwbXnZOCyGNVaPisHATBbmR", 
    timeout=20
)
model = "gpt-3.5-turbo-ca"


prompt1 = """
你是一个问题转述助手，你擅长将一个疑问句转为陈述句，现在你需要协助我完成任务

## 任务描述

我将提供一个问句，你需要假设该问题的答案是“<E>”（指的是用<E>符号作为答案），然后你根据答案自己总结一下，**同时保持原始信息的完整性**

## 任务要求

- 你需要充分发挥你的语言理解能力和语言整理能力，完成任务描述中的需求
- 你输出时使用的语言应该与问句的一致
- 请直接输出转换后的陈述句。禁止出现描述、解释、说明等文字。
- 以下是两个例子：
    问句：那个穿着黄色夹克衫的大胡子男人究竟是做什么工作的？
    输出：那个穿着黄色夹克衫的大胡子男人的工作是 <E> 。
    
    问句：哪个同学作为A班代表参加了校运会？
    输出：同学 <E> 作为A班代表参加了校运会。

## 问句如下：
"""


prompt2 = """
你是一个关系分析与提取助手，你擅长总结分析一句话中的实体关系，并能按要求总结为关系三元组

## 任务说明与定义
- 关系三元组的定义：是知识表示中用于描述事实的一种结构，形式为：(主语, 谓语, 宾语)，表示某个实体（主语subject）与另一个实体（宾语object）之间通过某种关系（谓语relation）连接起来的语义关系
- 我将提供一段文本，你的目标是找到文本中的全部关系三元组，并按格式要求输出
- 我提供的文本中会包含一个符号<E>，该符号实际上表示一个实体，且对于文本而言至关重要。你在提取关系三元组的过程中需要将这个符号<E>根据语境当作一个实体看待

## 要求
- 你提取的关系三元组由subject、relation、object组成，其中：
    - subject与object可以是单一的`名称`、`地点`、`时间`、`事件`、`行为`、`状态`；实体不可以是代词
    - relation通常是一个简单的短语。你需要充分发挥你的语言理解与总结能力，根据文本中的事实分析relation
    - 你提取的关系三元组需要具有连通性，这表示当一个实体存在多个关系时，你可以通过实体名称找到多个关系三元组记录。因此你需要避免出现使用不同名称来命名同一个实体的行为。
- 你在进行三元组提取是需要遵循以下逻辑：
    1. 联系上下文，将符号<E>当作一个实体。然后充分理解文本的内容，理解并记忆文本的信息
    2. 根据你的理解，选择文本中存在联系的两个实体作为subject和object
    3. 发挥你的语言总结能力，根据句子中的事实分析subject和object的关系
    4. 重复2-3步骤，直到你认为不存在新的关系三元组
- 你提取关系时使用的语言需要与文本的语言一致
- 我的输入中包含符号<E>，该符号是一个至关重要的实体，你在提取时<E>至少出现在一个关系三元组中
- 你需要尽可能多地寻找关系三元组，但不允许重复提取关系三元组

## 输出格式
- 你的输出应该是一个由多个字典组成的列表。一个字典代表一个关系三元组
- 字典包含4个key，其key与value的含义分别是：
    - subject: str类型，表示提取的关系元组中的主体
    - relation: str类型，表示主体与客体之间的关系（谓语）
    - object: str类型，表示提取的关系元组中的客体
- 以下是一个输出格式案例：
    [{"subject": "Romeo", "relation": "is lover", "object": "Juliet"}, ]
- 你需要根据格式要求输出列表。禁止出现描述、解释、说明等文字

## 例子:
input: "<E> is a coffee shop founded in Berkeley in 1982."
output: [{"subject": "<E>", "relation": "is", "object": "coffee shop"}, {"subject": "<E>", "relation": "founded in", "object": "Berkeley"}, {"subject": "<E>", "relation": "founded in", "object": "1982"}]

## 文本如下
"""

# question = "Which engineer is optimistic about the merger of Alpha Systems and Beta Innovate?"
question = "Which NFL team represented the AFC at Super Bowl 5"
# question = "哪支NFL球队代表AFC参加了超级碗50？"

# sentence = "The engineer who is optimistic about the merger of Alpha Systems and Beta Innovate is <E>"

def inference(content: str, is_json: bool = False):
    messages = [ChatCompletionUserMessageParam(content=content, role="user")]
    completion = client.chat.completions.create(
        messages=messages, model=model
    )
    response = completion.choices[0].message.content
    if is_json:
        return ast.literal_eval(response)
    return response

sentence = inference(prompt1 + question)
print(f"{question} -> {sentence}")
print(inference(prompt2 + sentence, is_json=True))
