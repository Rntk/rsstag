import logging
from typing import Optional
from pymongo import MongoClient, DESCENDING

class RssTagTags:
    indexes = ['owner', 'tag', 'unread_count', 'posts_count', 'processing']
    def __init__(self, db: MongoClient) -> None:
        self.db = db
        self.log = logging.getLogger('tags')

    def prepare(self) -> None:
        for index in self.indexes:
            try:
                self.db.posts.create_index(index)
            except Exception as e:
                self.log.warning('Can`t create index %s. May be already exists. Info: %s', e)

    def get_by_tag(self, owner: str, tag: str) -> Optional[dict]:
        query = {'owner': owner, 'tag': tag}
        try:
            tag = self.db.tags.find_one(query)
            if tag:
                result = tag
            else:
                result = {}
        except Exception as e:
            self.log.error('Can`t get tagby tag %s. User %s. Info: %s', tag, owner, e)
            result = None

        return result

    def get_by_regexp(self, owner: str, regexp: str, only_unread: Optional[bool]=None, projection: dict={}) -> Optional[list]:
        if only_unread:
            field_name = 'unread_count'
        else:
            field_name = 'posts_count'
        query = {
            'owner': owner,
            'tag': {'$regex': regexp, '$options': 'i'},
            field_name: {'$gt': 0},
        }
        limit = 50
        try:
            if projection:
                cursor = self.db.tags.find(query, projection=projection, limit=limit)
            else:
                cursor = self.db.tags.find(query, limit=limit)
            result = list(cursor)
        except Exception as e:
            self.log.error('Can`t search by regexp %s. User %s. Info: e', regexp, owner, e)
            result = None

        return result