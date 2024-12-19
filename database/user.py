import pymongo
from bson import ObjectId


# Initialization and reset
def connect(conn_str: str):
    """connect to the client and initialize mycol.  returns none."""
    global mycol
    client = pymongo.MongoClient(conn_str)
    db = client['CS518']
    mycol = db['user']
    return None


def reset():
    """reset the collection.  returns none."""
    global mycol
    mycol.drop()
    return None


# CRUD operations
def create_user(username: str, password: str, first_name: str, last_name: str, email: str) -> str:
    """Returns the ID of the new user."""

    global mycol
    user_data = {
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }
    result = mycol.insert_one(user_data)
    return str(result.inserted_id)


def read_user(id: str) -> dict:
    """returns user document"""

    global mycol
    return mycol.find_one({"_id": ObjectId(id)})


def read_users(query: dict) -> list:
    """returns a cursor of user documents matching the query"""

    global mycol
    return list(mycol.find(query))


def read_all_users():
    """Query MongoDB to get all users"""
    global mycol
    users = list(mycol.find())
    return users


def update_user(id, update):
    """update is dict with key / vals to update.
    returns updateresult."""

    global mycol
    return mycol.update_one({"_id": id}, {"$set": update})


def update_users(id, update):
    global mycol
    query = {"_id": ObjectId(id)}
    res_update = mycol.update_many(query, {"$set": update})
    return res_update.modified_count


def update_user_pass(username, newpass):
    """returns updateresult."""
    global mycol
    return mycol.update_one({"username": username}, {"$set": {"password": newpass}})


def delete_user(id: str):
    """returns deleteresult"""

    global mycol
    return mycol.delete_one({"_id": ObjectId(id)})


def get_username(user_id: str) -> str:
    """Retrieve the username based on the user_id."""
    global mycol
    user = mycol.find_one({"_id": ObjectId(user_id)}, {"username": 1})
    if user:
        return user.get("username", "")
    return ""