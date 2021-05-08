from ch_settings.celery import app as celery_app
from django.conf import settings
from .models import User, UserAddress
import pymongo

import logging

logger = logging.getLogger('general')


@celery_app.task(bind=True)
def save_to_mongodb(self, user_id):

    mongodb_client = pymongo.MongoClient(f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_CLUSTER_ADDRESS}")

    db = mongodb_client[settings.MONGODB_DATABASE_NAME]

    collection = db[settings.MONGODB_COLLECTION]
    get_user = User.objects.filter(id=user_id, is_active=True).first()
    get_address = UserAddress.objects.filter(user=get_user).first()

    collection.insert_one(
        {
            "id": get_user.id,
            "first_name": get_user.first_name,
            "last_name": get_user.last_name,
            "phone_no": get_user.phone_no,
            "email": get_user.email,
            "address_line_1": get_address.address_line_1 if get_address else "",
            "address_line_2": get_address.address_line_2 if get_address else "",
            "state": get_address.state if get_address else "",
            "city": get_address.city if get_address else "",
            "pincode": get_address.pincode if get_address else "",
            "location": {
                "type": "Point",
            "coordinates": [get_user.location[0]['lon'], get_user.location[0]['lat']]},
            "oxygen": get_user.oxygen,
            "remdesivir": get_user.remdesivir,
            "plasma": get_user.plasma,
            "user_type": get_user.user_type
        }
    )


@celery_app.task(bind=True)
def update_mongodb_data(self, user_id):

    mongodb_client = pymongo.MongoClient(f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_CLUSTER_ADDRESS}")

    db = mongodb_client[settings.MONGODB_DATABASE_NAME]

    collection = db[settings.MONGODB_COLLECTION]

    get_user = User.objects.filter(id=user_id).first()
    get_address = UserAddress.objects.filter(user=get_user).first()
    
    try:
        collection.update_one({'id': user_id}, 
        {
            "$set":
            {
                "first_name": get_user.first_name,
                "last_name": get_user.last_name,
                "phone_no": get_user.phone_no,
                "email": get_user.email,
                "address_line_1": get_address.address_line_1,
                "address_line_2": get_address.address_line_2,
                "state": get_address.state,
                "city": get_address.city,
                "pincode": get_address.pincode,
                "location": {
                    "type": "Point",
                    "coordinates": [get_user.location[0]['lon'], get_user.location[0]['lat']]
                },
                "oxygen": get_user.oxygen,
                "remdesivir": get_user.remdesivir,
                "plasma": get_user.plasma,
                "user_type": get_user.user_type
            }
        }, upsert=True)
    except Exception as ex:
        logger.error("Failed to update MongoDB")
        logger.error(ex)


@celery_app.task(bind=True)
def update_mongodb_collection(self):
    print ("update_mongodb_collection Started")
    mongodb_client = pymongo.MongoClient(f"mongodb+srv://{settings.MONGODB_USER}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_CLUSTER_ADDRESS}")

    db = mongodb_client[settings.MONGODB_DATABASE_NAME]

    collection = db[settings.MONGODB_COLLECTION]

    get_user = User.objects.all()

    for eu in get_user:
        get_address = UserAddress.objects.filter(user=eu).first()
        find_user = collection.find_one({'id': eu.id})
        user = {
                    "first_name": eu.first_name,
                    "last_name": eu.last_name,
                    "phone_no": eu.phone_no,
                    "email": eu.email,
                    "address_line_1": get_address.address_line_1 if get_address else "",
                    "address_line_2": get_address.address_line_2 if get_address else "",
                    "state": get_address.state if get_address else "",
                    "city": get_address.city if get_address else "",
                    "pincode": get_address.pincode if get_address else "",
                    "oxygen": eu.oxygen,
                    "remdesivir": eu.remdesivir,
                    "plasma": eu.plasma,
                    "user_type": eu.user_type
                }
        if eu.location:
            if 'lon' in eu.location[0] and 'lat' in eu.location[0]:
                user["location"] = {
                    "type": "Point",
                    "coordinates": [eu.location[0]['lon'], eu.location[0]['lat']]
                }
        if find_user:
            collection.update_one({'id': eu.id}, {'$set': user})
        else:
            user['id'] = eu.id
            collection.insert_one(user)
    print ("update_mongodb_collection Ended")
