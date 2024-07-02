from django.test import TestCase
import requests
from rest_framework import status

# Create your tests here.
BASE_URL = "http://127.0.0.1:9000/api"

class UeApiViewsTest(TestCase):
    """
    """

    def setUp(self):
        pass

    def test_list_ue(self):
        url = f"{BASE_URL}/ues"
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_ue(self):
        url = f"{BASE_URL}/ue/create"
        response = requests.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_ue(self):
        url = f"{BASE_URL}/ue/update/1"
        response = requests.put(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_ue(self):
        url = f"{BASE_URL}/ue/delete/1"
        response = requests.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_detail_ue(self):
        url = f"{BASE_URL}/ue/detail/1"
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)