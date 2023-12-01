from main.models import AnneeUniversitaire
from django.contrib.auth.models import Group, Permission
from main.helpers import get_authenticate_profile_path, get_user_role, get_id_authenticate_user_model



def bootstrap(request):
    create_groups_if_exist(request)
    current_annee_accademique = AnneeUniversitaire.static_get_current_annee_universitaire()
    auth_user_role = get_user_role(request)
    role_name = ""
    if auth_user_role:
        role_name = auth_user_role.name
    if role_name == "etudiant":
        etudiant = request.user.etudiant
        niveau = etudiant.get_niveau_annee(current_annee_accademique)[0]
    else:
        niveau = ''
        
    id_auth_model = get_id_authenticate_user_model(request)
    
    return {
        'annee_universitaire': current_annee_accademique if current_annee_accademique else "-",
        'annees_universitaire': AnneeUniversitaire.objects.all(),
        'auth_user_role': auth_user_role,
        'is_etudiant': role_name == 'etudiant',
        'is_directeur_des_etudes': role_name == 'directeur_des_etudes',
        'is_enseignant': role_name == 'enseignant',
        'is_secretaire': role_name == 'secretaire',
        'is_comptable': role_name == 'comptable',
        'id_authenticate_user_model': id_auth_model,
        'id_annee_selectionnee': int(request.session.get("id_annee_selectionnee")),
        'page_is_not_profil' : True,
        'profile_path': get_authenticate_profile_path(request, id_auth_model),
        'niveau': niveau,
        'MEDIA_URL' : '/media/',
    }


def create_groups_if_exist(request):
    permissions = [
        'view', 'add', 'change', 'delete', "diplome", "carte", "releve_details", "releve_synthetique",
    ]

    applications = "main"
    permissions_all_directeur_des_etudes = ["annee universitaire", "competence",
                                            "comptable", "conge", "Directeur des études",
                                            "domaine", "enseignant", "Etudiant", "evaluation",
                                            "fiche de paie", "information", "matiere", "note",
                                            "paiement", "parcours", "personnel", "programme",
                                            "salaire", "seance", "semestre", "tuteur", "ue"]

    permissions_directeur_des_etudes = {
        "view": permissions_all_directeur_des_etudes,
        "add": permissions_all_directeur_des_etudes,
        "change": permissions_all_directeur_des_etudes,
        "delete": permissions_all_directeur_des_etudes,
        "diplome": ["Etudiant"],
        "releve_details": ["Etudiant"],
        "releve_synthetique": ["Etudiant"],
        "carte": ["Etudiant"],
        "attestation": ["Etudiant"]

    }

    permissions_etudiant = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "seance"],
        "add": ["seance"],
        "change": ["seance"],
        "delete": [],
        "releve_details": ["etudiant"],
        "releve_synthetique": ["etudiant"],
    }

    permissions_enseignant = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "enseignant", "seance",],
        "add": ["evaluation", "note"],
        "change": ["evaluation", "note", "seance"],
        "delete": ["evaluation", "note"],
    }

    permissions_comptable = {
        "view": ["fiche de paie", "information", "personnel", "salaire", "etudiant", "enseignant", "tuteur"],
        "add": ["fiche de paie", "information", "salaire",],
        "change": ["fiche de paie", "information", "salaire",],
        "delete": [],
    }

    permissions_secretaire = {
        "view": ["etudiant", "matiere", "ue", "evaluation", "note", "enseignant", "seance", "tuteur"],
        "add": ["evaluation", "note", "seance", "ue", "matiere", "enseignant", "tuteur", "etudiant"],
        "change": ["evaluation", "note", "seance", "ue", "matiere", "enseignant", "tuteur", "etudiant"],
        "delete": ["evaluation", "note"],
        "releve_details": ["etudiant"],
        "releve_synthetique": ["etudiant"],
        "carte": ["etudiant"],
        "attestation": ["etudiant"]
    }

    groupe, is_created = Group.objects.get_or_create(
        name="directeur_des_etudes")
    if is_created:
        # Ajouter des permission
        add_permissions_to_groupe(groupe, permissions_directeur_des_etudes)

    groupe, is_created = Group.objects.get_or_create(name="etudiant")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_etudiant)

    groupe, is_created = Group.objects.get_or_create(name="enseignant")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_enseignant)

    groupe, is_created = Group.objects.get_or_create(name="comptable")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_comptable)

    groupe, is_created = Group.objects.get_or_create(name="secretaire")
    if is_created:
        add_permissions_to_groupe(groupe, permissions_secretaire)


def add_permissions_to_groupe(groupe, model_dictionnary):
    permissions_name = []
    for permission_key in model_dictionnary:
        permissions = model_dictionnary[permission_key]
        if permissions:
            for permission in permissions:
                permissions_name.append(permission_key+" "+permission)

    for name in permissions_name:
        try:
            permission = Permission.objects.filter(name__contains=name).get()
        except Exception as e:
            print(":::: Exception ::::")
        groupe.permissions.add(permission)
        