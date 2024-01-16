from django.db import models
from projet_ifnti import settings
from main.models import Semestre, Matiere, Enseignant

class Planning(models.Model):
    semaine = models.IntegerField()
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    datedebut = models.DateField()
    datefin = models.DateField()
    intervalle=models.CharField(null=True,max_length=50)
       
    def __str__(self):
        return f"Semaine {self.semaine} - {self.semestre}"
    
class SeancePlannifier(models.Model):
    intitule = models.CharField(max_length=200)
    date_heure_debut = models.DateTimeField()
    date_heure_fin = models.DateTimeField()
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    precision = models.CharField(max_length=255)
    professeur = models.ForeignKey(Enseignant, on_delete=models.CASCADE,null=True)
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE,null=True)
    valider = models.BooleanField(default=False)


