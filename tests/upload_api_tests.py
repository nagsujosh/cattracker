import unittest
import requests


class UploadApiTests(unittest.TestCase):

    def setUp(self):
        self.upload_url = 'not showing this time production hahaha'
        self.func_key = "not showing this time production hahaha"
        self.photo_path = '../static/assets/logo.png'
        self.uploaded_photo_id = None

    def test_upload_photo(self):
        with open(self.photo_path, 'rb') as photo_file:
            files = {'file': photo_file}
            res = requests.post(
                self.upload_url,
                params={"code": self.func_key},
                files=files
            )
            print("POST /upload", res.status_code, res.text)
            self.assertEqual(res.status_code, 201, "Failed to upload photo.")
            self.uploaded_photo_id = res.json().get('id')

    def test_verify_photo_upload(self):
        if not self.uploaded_photo_id:
            self.skipTest("Photo not uploaded, skipping verification test.")

        res = requests.get(
            f"{self.upload_url}{self.uploaded_photo_id}",
            params={"code": self.func_key}
        )
        print(f"GET /upload/{self.uploaded_photo_id}", res.status_code, res.text)
        self.assertEqual(res.status_code, 200, "Failed to verify uploaded photo.")

    def test_delete_photo(self):
        if not self.uploaded_photo_id:
            self.skipTest("Photo not uploaded, skipping delete test.")

        res = requests.delete(
            f"{self.upload_url}{self.uploaded_photo_id}",
            params={"code": self.func_key}
        )
        print(f"DELETE /upload/{self.uploaded_photo_id}", res.status_code, res.text)
        self.assertIn(res.status_code, [200, 204], "Failed to delete photo.")

    def test_verify_photo_deletion(self):
        if not self.uploaded_photo_id:
            self.skipTest("Photo not uploaded, skipping deletion verification test.")

        res = requests.get(
            f"{self.upload_url}{self.uploaded_photo_id}",
            params={"code": self.func_key}
        )
        print(f"GET /upload/{self.uploaded_photo_id} after delete", res.status_code, res.text)
        self.assertEqual(res.status_code, 404, "Photo should not exist after deletion.")


if __name__ == '__main__':
    unittest.main()
