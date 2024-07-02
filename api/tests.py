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
        response = requests.get(url)
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



class MatiereApiViewsTest(TestCase):
    """
    MatiereApiViewsTest contient les methodes de test du crud de matiere_api_views
    """

    def setUp(self):
        pass    

    def test_list_matiere(self):
        url = f"{BASE_URL}/matieres"
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_matiere(self):
        url = f"{BASE_URL}/matiere/create"
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_update_matiere(self):
        url = f"{BASE_URL}/matiere/update/1"
        response = requests.put(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_matiere(self):
        url = f"{BASE_URL}/matiere/delete/1"
        response = requests.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_detail_matiere(self):
        url = f"{BASE_URL}/matiere/detail/1"
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PersonnelTest(TestCase):
    """
    Test routes personnels
    """

    def setUp(self):
        pass

    def test_list_personnel(self):
        url=f"{BASE_URL}/personnels"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    def test_create_personnel(self):
        url=f"{BASE_URL}/personnel/create"
        response=requests.post(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    def test_delete_personnel(self):
        url=f"{BASE_URL}/personnel/delete/12"
        response=requests.delete(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_update_personnel(self):
        url=f"{BASE_URL}/personnel/update/1"
        response=requests.put(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_detail_personnel(self):
        url=f"{BASE_URL}/personnel/detail/4"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_form_demander_conge(self):
        url=f"{BASE_URL}/personnel/form__demander_conge"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_imprimer_demande_conge(self):
        url=f"{BASE_URL}/personnel/imprimer_demande_conge"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    

    def test_accorder_conge(self):
        url=f"{BASE_URL}/personnel/accorder_conge"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    

