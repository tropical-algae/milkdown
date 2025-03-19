import asyncio
from itertools import chain
# from datasets import load_dataset

from milkdown.app.services.extract_task.extract_doc import extract_paragraph_relation_tuple

candicate = ['所在城市', '朝代', '父亲', '出品公司', '作词', '注册资本', '面积', '祖籍', '母亲', '上映时间', '成立日期', '歌手', '丈夫', '妻子', '连载网站', '身高', '主角', '修业年限', '总部地点', '字', '简称', '人口数量', '目', '国籍', '民族', '所属专辑', '号', '作者', '气候', '出生地', '作曲', '编剧', '占地面积', '制片人', '出生日期', '毕业院校', '导演', '海拔', '出版社', '改编自', '首都', '嘉宾', '主持人', '创始人', '董事长', '主演']
# candicate = ['主演']

# num = 20


# ds = load_dataset("xusenlin/duie",cache_dir="./cache")

# candicate = list({i["predicate"] for i in  list(chain.from_iterable(ds["validation"][:num]["spo_list"]))})

# for data in ds["validation"]:
#     pass
# print(len(ds))

asyncio.run(
    extract_paragraph_relation_tuple("如何演好自己的角色，请读《演员自我修养》《喜剧之王》周星驰崛起于穷困潦倒之中的独门秘笈", candicate)
)