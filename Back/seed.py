from dotenv import load_dotenv
from app.database.session import SessionLocal
from app.models import User, Materiel
from app.core.security import get_password_hash


# Charger les variables du fichier .env
load_dotenv()


def seed_database():
    db = SessionLocal()

    try:
        # ============================================================
        # 1. CREATION DE L'ADMINISTRATEUR
        # ============================================================

        admin_email = "collopolo085@gmail.com"

        admin = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        if not admin:
            admin = User(
                email=admin_email,
                mot_de_passe_hache=get_password_hash("Admin123!"),
                nom_complet="Administrateur InfoTech",
                departement="Informatique",
                poste="Administrateur",
                role="administrateur",
                statut="approuve",
            )

            db.add(admin)
            db.commit()
            db.refresh(admin)

            print("✅ Administrateur créé.")
        else:
            print("ℹ️ Administrateur déjà existant.")

        # ============================================================
        # 2. CREATION D'UN UTILISATEUR DE TEST
        # ============================================================

        user_email = "gnimadikimberly@gmail.com"

        user = (
            db.query(User)
            .filter(User.email == user_email)
            .first()
        )

        if not user:
            user = User(
                email=user_email,
                mot_de_passe_hache=get_password_hash("User123!"),
                nom_complet="Jean Kouassi",
                departement="Informatique",
                poste="Développeur",
                role="utilisateur",
                statut="approuve",
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            print("✅ Utilisateur de test créé.")
        else:
            print("ℹ️ Utilisateur de test déjà existant.")

        # ============================================================
        # 3. CREATION DES MATERIELS
        # ============================================================

        materiels = [
            {
                "nom": "Dell Latitude 5420",
                "categorie": "Ordinateur",
                "description": "Ordinateur portable professionnel Dell Latitude 5420.",
                "quantite_totale": 10,
                "quantite_disponible": 7,
                "statut": "disponible",
            },
            {
                "nom": "HP ProBook 450 G8",
                "categorie": "Ordinateur",
                "description": "Ordinateur portable professionnel HP ProBook 450 G8.",
                "quantite_totale": 8,
                "quantite_disponible": 6,
                "statut": "disponible",
            },
            {
                "nom": "Écran Dell 24 pouces",
                "categorie": "Périphérique",
                "description": "Écran professionnel Dell 24 pouces Full HD.",
                "quantite_totale": 15,
                "quantite_disponible": 12,
                "statut": "disponible",
            },
            {
                "nom": "Clavier Logitech",
                "categorie": "Accessoire",
                "description": "Clavier USB Logitech pour poste informatique.",
                "quantite_totale": 20,
                "quantite_disponible": 17,
                "statut": "disponible",
            },
            {
                "nom": "Souris Logitech",
                "categorie": "Accessoire",
                "description": "Souris USB Logitech.",
                "quantite_totale": 25,
                "quantite_disponible": 22,
                "statut": "disponible",
            },
            {
                "nom": "Casque Logitech",
                "categorie": "Accessoire",
                "description": "Casque audio avec microphone.",
                "quantite_totale": 12,
                "quantite_disponible": 10,
                "statut": "disponible",
            },
            {
                "nom": "Webcam Logitech",
                "categorie": "Périphérique",
                "description": "Webcam USB pour visioconférences.",
                "quantite_totale": 8,
                "quantite_disponible": 7,
                "statut": "disponible",
            },
            {
                "nom": "Vidéoprojecteur Epson",
                "categorie": "Audiovisuel",
                "description": "Vidéoprojecteur professionnel Epson.",
                "quantite_totale": 3,
                "quantite_disponible": 2,
                "statut": "disponible",
            },
           
            {
                "nom": "Onduleur APC",
                "categorie": "Énergie",
                "description": "Onduleur APC pour protection des équipements informatiques.",
                "quantite_totale": 6,
                "quantite_disponible": 5,
                "statut": "disponible",
            },
        ]

        for data in materiels:
            materiel_existant = (
                db.query(Materiel)
                .filter(Materiel.nom == data["nom"])
                .first()
            )

            if not materiel_existant:
                materiel = Materiel(
                    nom=data["nom"],
                    categorie=data["categorie"],
                    description=data["description"],
                    quantite_totale=data["quantite_totale"],
                    quantite_disponible=data["quantite_disponible"],
                    statut=data["statut"],
                    cree_par_admin_id=admin.id,
                )

                db.add(materiel)

                print(f"✅ Matériel créé : {data['nom']}")
            else:
                print(f"ℹ️ Matériel déjà existant : {data['nom']}")

        db.commit()

        print("\n====================================")
        print("SEED TERMINÉ AVEC SUCCÈS")
        print("====================================")
        print()
        print("Compte administrateur :")
        print("Email      : admin@infotech.com")
        print("Mot de passe : Admin123!")
        print()
        print("Compte utilisateur :")
        print("Email      : user@infotech.com")
        print("Mot de passe : User123!")
        print()
        print("10 matériels de test ont été ajoutés.")

    except Exception as e:
        db.rollback()
        print(" Une erreur est survenue :")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()