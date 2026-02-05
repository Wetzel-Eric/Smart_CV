def qualify_need() -> str:
    print("Avant de continuer, 3 questions rapides :\n")
    pain = input("1) Problème principal ?\n> ")
    time = input("2) Horizon d’opérationnalité ?\n> ")
    success = input("3) Succès dans 6 mois ?\n> ")
    return f"Pain: {pain}\nTemporalité: {time}\nCritères de succès: {success}"
