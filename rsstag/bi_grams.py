import logging
from typing import Optional
from pymongo import MongoClient, DESCENDING

class RssTagBiGrams:
    indexes = ['owner', 'tag', 'tags', 'unread_count', 'posts_count']
    def __init__(self, db: MongoClient) -> None:
        self.db = db
        self.log = logging.getLogger('bi_grams')

    def prepare(self) -> None:
        for index in self.indexes:
            try:
                self.db.posts.create_index(index)
            except Exception as e:
                self.log.warning('Can`t create index %s. May be already exists. Info: %s', e)

    def get_by_bi_gram(self, owner: str, bi_gram: str) -> Optional[dict]:
        query = {'owner': owner, 'tag': bi_gram}
        try:
            db_bi_gram = self.db.bi_grams.find_one(query)
            if db_bi_gram:
                result = db_bi_gram
            else:
                result = {}
        except Exception as e:
            self.log.error('Can`t get bi-gram %s. User %s. Info: %s', bi_gram, owner, e)
            result = None

        return result

    def get_by_tags(self, owner: str, tags: list, only_unread: Optional[bool]=None, projection: dict={}) -> Optional[list]:
        query = {
            'owner': owner,
            'tags': {'$all': tags}
        }
        sort_data = []
        if only_unread:
            query['unread_count'] = {'$gt': 0}
            sort_data.append(('unread_count', DESCENDING))
        else:
            sort_data.append(('posts_count', DESCENDING))
        try:
            if projection:
                cursor = self.db.bi_grams.find(query, projection=projection).sort(sort_data)
            else:
                cursor = self.db.bi_grams.find(query).sort(sort_data)
            result = list(cursor)
        except Exception as e:
            self.log.error('Can`t get tagby tag %s. User %s. Info: %s', tags, owner, e)
            result = None

        return result

