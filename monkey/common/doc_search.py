
###
# author liuxing
#  email 1747411761@qq.com
#  date  2020/11/18 20:10:11
###

import asyncio

import pymongo

import sys
sys.path.append("..")

from common.common_tools import gen_stop_words, text_seg
from database.motor_base import MotorBase
from utils.log import logger

stop_words = gen_stop_words()


async def doc_search(*, query: str, mongo_db=None) -> list:
    """
    布尔查询
    :param query:
    :return:
    """
    result = []
    try:
        if mongo_db is None:
            mongo_db = MotorBase().get_db()
        seg_query = text_seg(text=query, stop_words=stop_words)
        query_list, word_id_list, doc_id_list, final_query_list = [], [], [], []

        for each_word in seg_query:
            query_list.append({
                'word': each_word
            })

        # 分词的词组转化成单词id 单词id最好加载到内存中 节省一次数据库查询
        word_cursor = mongo_db.word_id.find(
            {"$or": query_list},
            {'word_id': 1, '_id': 0}
        )

        async for word in word_cursor:
            word_id_list.append(word)

        # 根据单词id找出文档
        index_cursor = mongo_db.inverted_index.find(
            {"$or": word_id_list},
            {'inverted_list': 1, 'word_tf': 1, '_id': 0}
        )

        async for index in index_cursor:
            cur_doc_id = 0
            # 将倒排列表数据加载进内存
            for i in index['inverted_list']:
                cur_doc_id += i[0]
                doc_id_list.append(cur_doc_id)
        print(doc_id_list)
        # 根据文档id 找出文档详细信息
        for each_doc in set(doc_id_list):
            final_query_list.append({
                'doc_id': each_doc
            })

        doc_cursor = mongo_db.doc_id.find(
            {"$or": final_query_list},
            {"_id": 0}
        )

        async for doc in doc_cursor:
            result.append(doc)

    except pymongo.errors.OperationFailure as e:
        logger.error(e)

    except Exception as e:
        logger.error(e)

    return result


if __name__ == '__main__':
    res = asyncio.get_event_loop().run_until_complete(doc_search(query='python'))
    for each in res:
        print(each['title'])
