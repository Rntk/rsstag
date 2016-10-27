import logging
from rsstag.utils import get_coords_yandex, load_config
from rsstag.tags import RssTagTags
from pymongo import MongoClient


def make_tags_geo(db: MongoClient, key: str):
    tags = RssTagTags(db)
    users_cur = db.users.find({})
    for user in users_cur:
        owner = user['sid']
        tags_cities = tags.get_city_tags(owner)
        if tags_cities:
            tag_coord = []
            for tag in tags_cities:
                try:
                    tag_coord = get_coords_yandex(tag['city']['c']['t'], tag['city']['t'], key=key)
                    if tag_coord and len(tag_coord) > 1:
                        db.tags.update_one(
                            {'tag': tag['tag'], 'owner': owner},
                            {'$set' : {'city.co': tag_coord}}
                        )
                    else:
                        logging.error('Wrong city %s coords. User: %s. Info: %s', tag['tag'], owner, tag_coord)
                except Exception as e:
                    logging.error(
                        'Can`t get coords for city %s. User: %s. Coords %s. Info: %s', tag['tag'],
                        owner,
                        tag_coord,
                        e
                    )
        else:
            logging.error('Cities coords not maked. User: %s. Cities: %s', owner, tags_cities)

        del tags_cities
        tags_countries = tags.get_country_tags(owner)
        if tags_countries:
            tag_coord = []
            for tag in tags_countries:
                try:
                    tag_coord = get_coords_yandex(tag['country']['t'], key=key)
                    if tag_coord and len(tag_coord) > 1:
                        db.tags.update_one(
                            {'tag': tag['tag'], 'owner': owner},
                            {'$set': {'country.co': tag_coord}}
                        )
                    else:
                        logging.error('Wrong country %s coords. User: %s. Info: %s', tag['tag'], owner, tag_coord)
                except Exception as e:
                    logging.error('Can`t get coords for country %s. User: %s. Info: %s', tag['tag'], owner, e)
        else:
            logging.error('Country coords not maked. User: %s. Cities: %s', owner, tags_cities)

if __name__ == '__main__':
    config = load_config('./rsscloud.conf')
    logging.basicConfig(
        filename=config['settings']['log_file'],
        filemode='a',
        level=getattr(logging, config['settings']['log_level'].upper())
    )
    cl = MongoClient(config['settings']['db_host'], int(config['settings']['db_port']))
    db = cl.rss
    make_tags_geo(db, config['yandex']['geocode_key'])