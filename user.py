import requests
from flask_login import UserMixin

# API URL and function key for the user service
user_url = 'not showing this time production hahaha'
func_key = "not showing this time production hahaha"


class User(UserMixin):
    def __init__(self, user_id, username, email, first_name, last_name, photo=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get(user_id):
        try:
            response = requests.get(f"{user_url}{user_id}", params={"code": func_key})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching user: {e}")
            return None

        data = response.json()
        user_id = data.get('_id', {}).get('$oid')
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        photo = data.get('photo')
        return User(user_id, username, email, first_name, last_name, photo) if user_id and username else None

    @staticmethod
    def authenticate(username_or_email, password):
        try:
            response = requests.get(
                user_url,
                params={"code": func_key, "username": username_or_email, "password": password}
            )
            if response.status_code == 404:
                response = requests.get(
                    user_url,
                    params={"code": func_key, "email": username_or_email, "password": password}
                )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error authenticating user: {e}")
            return None

        data = response.json()
        user_id = data.get('_id', {}).get('$oid')
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        photo = data.get('photo')
        return User(user_id, username, email, first_name, last_name, photo) if user_id else None

    def check_password(self, password):
        try:
            response = requests.get(
                user_url,
                params={"code": func_key, "username": self.username, "password": password}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error checking password: {e}")
            return False

        return response.status_code == 200
