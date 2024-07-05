from django.test import TestCase
import requests
from rest_framework import status

from main.models import Personnel

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

   

class PersonnelApiTest(TestCase):
    """
    Test routes personnels
    """

    def setUp(self):
        pass
        #Personnel.objects.all().delete()
        
    # def test_list_personnel(self):
    #     url=f"{BASE_URL}/personnels"
    #     response=requests.get(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)
    # def test_create_personnel(self):
    #     Personnel.objects.all().delete()
    #     data = {
    #         'nom': 'toutabiz','prenom': 'alibaba',
    #         "datenaissance":"1998-02-04","sexe":"M",
    #         "lieunaissance":"kara","contact":"90789502",
    #         "email":"toub@gmail.com","adresse":"sokode",
    #         "prefecture":"tchaoudjo","carte_identity":45896,
    #         "nationalite":"togolaise","salaireBrut":10000,
    #         "nbreJrsCongesRestant":30,"nbreJrsConsomme":8,
    #         "qualification_professionnel":"Enseignant",
    #         "nombre_de_personnes_en_charge":2,"nif":"148950",
    #         "numero_cnss":"982200478",
    #     }
        
    #     url=f"{BASE_URL}/personnel/create"
    #     response=requests.post(url,data)
    #     self.assertEqual(response.status_code,status.HTTP_201_CREATED)
    #     self.assertEqual(Personnel.objects.count(), 1)
        
        
        
        
    # def test_delete_personnel(self):
    #     url=f"{BASE_URL}/personnel/delete/19"
    #     response=requests.delete(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)

    # def test_update_personnel(self):
    #     url=f"{BASE_URL}/personnel/update/23"
    #     response=requests.put(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)

    # def test_detail_personnel(self):
    #     url=f"{BASE_URL}/personnel/detail/4"
    #     response=requests.get(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)

    
    
class EnseignantApiTest(TestCase):
    def setUp(self):
        pass
    def test_create_enseignant(self):
        url=f"{BASE_URL}/enseignant/create"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_update_enseignant(self):
        url=f"{BASE_URL}/enseignant/update/2"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    

    def test_delete_enseignant(self):
        url=f"{BASE_URL}/enseignant/delete/2"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_list_enseignant(self):
        url=f"{BASE_URL}/enseignants"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
    
    def test_detail_enseignant(self):
        url=f"{BASE_URL}/enseignant/detail/2"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    
    def test_detail_enseignant(self):
        url=f"{BASE_URL}/enseignant/detail/2"
        response=requests.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    
class CongeTestApiViews(TestCase):
    def setUp(self):
        pass
    
    # def test_formulaire_demande_conges(self):
    #     url=f"{BASE_URL}/personnel/form__demander_conge/1"
    #     response=requests.get(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)

    # def test_imprimer_demande_conge(self):
    #     url=f"{BASE_URL}/personnel/imprimer_demande_conge"
    #     response=requests.get(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)
    

    # def test_accorder_conge(self):
    #     url=f"{BASE_URL}/personnel/accorder_conge"
    #     response=requests.get(url)
    #     self.assertEqual(response.status_code,status.HTTP_200_OK)