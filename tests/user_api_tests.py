import unittest
import json
import requests

user_url = 'not showing this time production hahaha'
func_key = "not showing this time production hahaha"

points = 0


class TestUserMethods(unittest.TestCase):

    def test_CRUD_user(self):
        global points
        print('Testing CRUD operations for User API')

        # Create a new user (POST)
        user_data = {
            "username": "dave2",
            "password": "evad",
            "email": "dave2@example.com",
            "first_name": "Dave",
            "last_name": "Smith",
        }
        res = requests.post(
            user_url,
            params={"code": func_key},
            json=user_data
        )
        print("POST /user", res.status_code, res.text)
        self.assertIn(res.status_code, [200, 201])

        _id = res.text
        self.assertIsNotNone(_id, "User creation failed: No user_id returned.")
        points += 1

        # Retrieve user by username (GET with filter)
        res = requests.get(
            user_url,
            params={"code": func_key, "username": "dave2", "password": "evad"}
        )
        print("GET /user by username", res.status_code, res.text)
        self.assertEqual(res.status_code, 200)
        u = res.json()
        self.assertEqual(u.get("username"), "dave2")
        points += 1

        # Update the user's email
        update_data = {
            "email": "dave2_updated@example.com"
        }
        res = requests.put(
            f"{user_url}{_id}",
            params={"code": func_key},
            json=update_data
        )
        print(f"PUT /user/{_id}", res.status_code, res.text)
        self.assertEqual(res.status_code, 200, "Failed to update user.")
        points += 1

        # Retrieve the updated user (GET)
        res = requests.get(
            f"{user_url}{_id}",
            params={"code": func_key}
        )
        print(f"GET /user/{_id} after update", res.status_code, res.text)
        self.assertEqual(res.status_code, 200)
        updated_user = res.json()
        self.assertEqual(updated_user.get("email"), "dave2_updated@example.com")
        points += 1

        # Delete the user (DELETE)
        res = requests.delete(
            f"{user_url}{_id}",
            params={"code": func_key}
        )
        print(f"DELETE /user/{_id}", res.status_code, res.text)
        self.assertIn(res.status_code, [200, 204], "Failed to delete user.")
        points += 1

        # Verify the user no longer exists (GET)
        res = requests.get(
            f"{user_url}{_id}",
            params={"code": func_key}
        )
        print(f"GET /user/{_id} after delete", res.status_code, res.text)
        self.assertEqual(res.status_code, 404, "User should not exist.")
        points += 1

    def test_print_points(self):
        print("Total Points:", points)


if __name__ == '__main__':
    unittest.main()
