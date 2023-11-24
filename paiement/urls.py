from django.urls import path
from . import views

app_name = 'paiement'

urlpatterns = [



                        #### Compte bancaire ####
    path('etat_compte_bancaire/<int:id_annee_selectionnee>/<int:compte_bancaire_id>/', views.etat_compte_bancaire, name='etat_compte_bancaire'),
    path('compte_bancaire/<int:id_annee_selectionnee>/', views.compte_bancaire, name='compte_bancaire'),
    path('create_compte/', views.create_compte, name='create_compte'),


                             #### Frais ####
    path('liste_frais/<int:id_annee_selectionnee>/', views.liste_frais, name='liste_frais'),
    path('enregistrer_frais/', views.enregistrer_frais, name='enregistrer_frais'),
    path('modifier_frais/<int:id>/', views.enregistrer_frais, name='modifier_frais'),



                            #### Comptable ####
    path('create_comptable/', views.create_comptable, name='create_comptable'),
    path('comptable_detail/(?P<id>[0-9]+)\\Z/', views.comptable_detail, name='comptable_detail'),
    path('edit_comptable/(?P<id>[0-9]+)\\Z/', views.create_comptable, name='edit_comptable'),
    path('comptable_list/<int:id_annee_selectionnee>/', views.comptable_list, name='comptable_list'),
    path('comptables_suspendu/', views.comptables_suspendu, name='comptables_suspendu'),


                            #### Paiement ####
    path('liste_paiements/<int:id_annee_selectionnee>/', views.liste_paiements, name='liste_paiements'),
    path('enregistrer_paiement/', views.enregistrer_paiement, name='enregistrer_paiement'),
    path('etat_paiements/<str:id>/<int:id_annee_selectionnee>/', views.etat_paiements, name='etat_paiements'),
    path('modifier_paiement/<int:id>/', views.enregistrer_paiement, name='modifier_paiement'),

                        ##### Bilan ######
    path('liste_etudiants/<int:id_annee_selectionnee>/', views.liste_etudiants, name='liste_etudiants'),
    path('bilan_paiements_annuel/<int:id_annee_selectionnee>/', views.bilan_paiements_annuel, name='bilan_paiements_annuel'),


                          #### Bulletin de paye #### 
    path('bulletins_de_paye/<int:id_annee_selectionnee>/', views.les_bulletins_de_paye, name='bulletins_de_paye'),
    path('enregistrer_bulletin/', views.enregistrer_bulletin, name='enregistrer_bulletin'),
    path('modifier_bulletin/<int:id>/', views.enregistrer_bulletin, name='modifier_bulletin'),
    path('detail_bulletin/<int:id>/', views.detail_bulletin, name='detail_bulletin'),
    path('bulletin_de_paye/<int:id>/', views.bulletin_de_paye, name='bulletin_de_paye'),


                            #### Paiement des fournisseurs ####
    path('liste_paiements_fournisseurs/<int:id_annee_selectionnee>/', views.liste_paiements_fournisseurs, name='liste_paiements_fournisseurs'),
    path('enregistrer_paiement_fournisseur/', views.enregistrer_paiement_fournisseur, name='enregistrer_paiement_fournisseur'),
    path('modifier_paiement_fournisseur/<int:id>/', views.enregistrer_paiement_fournisseur, name='modifier_paiement_fournisseur'),

                          
                            #### Fiche de Paie ####                        
    path('liste_fiches_de_paie/<int:id_annee_selectionnee>/', views.liste_fiches_de_paie, name='liste_fiches_de_paie'),
    path('enregistrer_fiche_de_paie/', views.enregistrer_fiche_de_paie, name='enregistrer_fiche_de_paie'),
    path('modifier_fiche_de_paie/<int:id>/', views.enregistrer_fiche_de_paie, name='modifier_fiche_de_paie'),
    path('fiche_paie/<int:id>/', views.fiche_paie, name='fiche_paie'),
    

                             #### Fiche de Prise en charge ####                        
    path('liste_fiches_de_prise_en_charge/<int:id_annee_selectionnee>/', views.liste_fiches_de_prise_en_charge, name='liste_fiches_de_prise_en_charge'),
    path('enregistrer_fiche_de_prise_en_charge/', views.enregistrer_fiche_de_prise_en_charge, name='enregistrer_fiche_de_prise_en_charge'),
    path('modifier_fiche_de_prise_en_charge/<int:id>/', views.enregistrer_fiche_de_prise_en_charge, name='modifier_fiche_de_prise_en_charge'),
    path('fiche_de_charge/<int:id>/', views.fiche_de_charge, name='fiche_de_charge'),
    
    

]