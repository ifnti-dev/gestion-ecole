from django.db import models
from main.models import Semestre, Matiere, Enseignant

class Planning(models.Model):
    intitule = models.CharField(max_length=200)
    semaine = models.CharField(max_length=10)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    date_heure_debut = models.DateTimeField()
    date_heure_fin = models.DateTimeField()
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    precision = models.CharField(max_length=255)
    professeur = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    valider = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.matiere} - {self.professeur} - {self.semaine} - {self.semestre}"
