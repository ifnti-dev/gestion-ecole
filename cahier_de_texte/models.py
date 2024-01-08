from django.db import models
from main.models import Etudiant,Matiere,Semestre,Enseignant
from planning.models import SeancePlannifier

class Seance(models.Model):
    intitule = models.CharField(max_length=200)
    date_et_heure_debut = models.DateTimeField()
    date_et_heure_fin = models.DateTimeField()
    description = models.TextField()
    auteur = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='seance_auteur', default='Anonyme')
    valider = models.BooleanField(default=False)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.SET_NULL, null=True)
    commentaire = models.TextField(null=True)
    eleves_presents = models.ManyToManyField(Etudiant, related_name='seances_presents')
    seancePlannifier=models.ForeignKey(SeancePlannifier,on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.intitule
    
    class meta :
        unique_together=["date_et_heure_debut","date_et_heure_fin","semestre"]

