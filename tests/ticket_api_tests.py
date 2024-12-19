import unittest
import json
import requests

ticket_url = 'not showing this time production hahaha'
func_key = "not showing this time production hahaha"


class TestTicketMethods(unittest.TestCase):

    def test_CRUD_ticket(self):
        print('Testing CRUD operations for Ticket API')

        # Create a new ticket (POST)
        res = requests.post(
            ticket_url,
            params={"code": func_key},
            json={
                "user_id": "123",
                "lost": True,
                "lost_item": "Laptop",
                "description": "Black Dell XPS",
                "location_lost": "Library"
            }
        )
        print("POST /ticket", res.status_code, res.text)
        self.assertIn(res.status_code, [200, 201])
        ticket_id = json.loads(res.text).get("ticket_id")
        self.assertIsNotNone(ticket_id, "Failed to create a ticket - no ticket_id returned.")

        # Retrieve the ticket by ID (GET)
        res = requests.get(f"{ticket_url}/{ticket_id}", params={"code": func_key})
        print(f"GET /ticket/{ticket_id}", res.status_code, res.text)
        self.assertEqual(res.status_code, 200)
        ticket_data = res.json()
        self.assertEqual(ticket_data.get("lost_item"), "Laptop")
        self.assertEqual(ticket_data.get("description"), "Black Dell XPS")

        # Update the ticket (PUT)
        res = requests.put(
            f"{ticket_url}/{ticket_id}",
            params={"code": func_key},
            json={"description": "Black Dell XPS 13"}
        )
        print(f"PUT /ticket/{ticket_id}", res.status_code, res.text)
        self.assertIn(res.status_code, [200, 204])

        # Retrieve the updated ticket (GET)
        res = requests.get(f"{ticket_url}/{ticket_id}", params={"code": func_key})
        print(f"GET /ticket/{ticket_id} after update", res.status_code, res.text)
        self.assertEqual(res.status_code, 200)
        ticket_data = res.json()
        self.assertEqual(ticket_data.get("description"), "Black Dell XPS 13")

        # Delete the ticket (DELETE)
        res = requests.delete(f"{ticket_url}/{ticket_id}", params={"code": func_key})
        print(f"DELETE /ticket/{ticket_id}", res.status_code, res.text)
        self.assertIn(res.status_code, [200, 204])

        # Verify the ticket no longer exists (GET)
        res = requests.get(f"{ticket_url}/{ticket_id}", params={"code": func_key})
        print(f"GET /ticket/{ticket_id} after delete", res.status_code, res.text)
        self.assertEqual(res.status_code, 404, "Deleted ticket still retrievable.")

    def test_print_points(self):
        print("Tests completed successfully.")


if __name__ == '__main__':
    unittest.main()
