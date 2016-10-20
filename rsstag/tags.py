import logging
from typing import Optional
from pymongo import MongoClient, DESCENDING, UpdateOne

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
            db_tag = self.db.tags.find_one(query)
            if db_tag:
                result = db_tag
            else:
                result = {}
        except Exception as e:
            self.log.error('Can`t get tag %s. User %s. Info: %s', tag, owner, e)
            result = None

        return result

    def get_by_tags(self, owner: str, tags: list, only_unread: Optional[bool]=None, projection: dict={}) -> Optional[list]:
        query = {
            'owner': owner,
            'tag': {'$in': tags}
        }
        if only_unread:
            query['unread_count'] = {'$gt': 0}
        try:
            if projection:
                cursor = self.db.tags.find(query, projection=projection)
            else:
                cursor = self.db.tags.find(query)
            result = list(cursor)
        except Exception as e:
            self.log.error('Can`t get tagby tag %s. User %s. Info: %s', tags, owner, e)
            result = None

        return result

    def get_all(self, owner: str, only_unread: Optional[bool]=None, hot_tags: bool=False,
                opts: dict=[], projection: dict={}) -> Optional[list]:
        query = {'owner': owner}
        if 'regexp' in opts:
            query['tag'] = {'$regex': opts['regexp'], '$options': 'i'}
        sort_data = []
        if hot_tags:
            sort_data.append(('temperature', DESCENDING))
        if only_unread:
            sort_data.append(('unread_count', DESCENDING))
            query['unread_count'] = {'$gt': 0}
        else:
            sort_data.append(('posts_count', DESCENDING))
        params = {}
        if 'offset' in opts:
            params['skip'] = opts['offset']
        if 'limit' in opts:
            params['limit'] = opts['limit']
        if projection:
            params['projection'] = projection
        try:
            cursor = self.db.tags.find(query, **params).sort(sort_data)
            result = list(cursor)
        except Exception as e:
            self.log.error('Can`t get all tags user %s. Info: %s', owner, e)
            result = None

        return result

    def count(self, owner: str, only_unread: Optional[bool]=None, regexp: str='') -> Optional[int]:
        query = {'owner': owner}
        if regexp:
            query['tag'] = {'$regex': regexp, '$options': 'i'}
        if only_unread:
            query['unread_count'] = {'$gt': 0}
        try:
            result = self.db.tags.count(query)
        except Exception as e:
            self.log.error('Can`t get tags number for user %s. Info: e', owner, e)
            result = None

        return result

    def change_unread(self, owner: str, tags: dict, readed: bool) -> Optional[bool]:
        find_query = {'owner': owner}
        updates = []
        result = False
        inc_query = {'unread_count': 0}
        for tag in tags:
            find_query['tag'] = tag
            inc_query['unread_count'] = -tags[tag] if readed else tags[tag]
            updates.append(UpdateOne(find_query, {'$inc': inc_query}))
        if updates:
            try:
                bulk_result = self.db.tags.bulk_write(updates, ordered=False)
                result = (bulk_result.matched_count > 0)
            except Exception as e:
                result = None
                self.log.error('Can`t change unread_count for tags. User %s. info: %s', owner, e)

        return result