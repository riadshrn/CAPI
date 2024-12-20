import os
import sys
import json
import unittest

from App import app, BASE_DIR, parties

class PlanningPokerTestCase(unittest.TestCase):

    def setUp(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tSetup: Initialisation de l'environnement de test.\n\n")
        self.app = app.test_client()
        self.app.testing = True

        os.makedirs(os.path.join(BASE_DIR, "partie_sauvegardee"), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR, "resultats"), exist_ok=True)

    def test_index(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Vérification de la page d'accueil.\n\n")
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Planning Poker", response.data)
        print("-> Page d'accueil fonctionne correctement.")

    def test_configure_party(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Création d'une partie.\n\n")
        response = self.app.post('/configure', data={
            'mode_de_jeu': 'moyenne',
            'nombre_joueurs': 5,
            'player_0': 'host_player'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(len(parties) > 0)
        print("-> Partie créée avec succès, mode de jeu:", 'moyenne')


    def test_join_party(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Rejoindre une partie.\n\n")
        self.test_configure_party()
        code = list(parties.keys())[0]

        response = self.app.post('/join_party', data={
            'party_code': code,
            'player_name': 'player2'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('player2', parties[code]['joueurs'])
        print("-> Le joueur 'player2' a rejoint la partie avec succès.")

    def test_save_and_load_state(self):
        print("\n\n----------------------------------------------------------------------")
        # Configuration de la partie
        self.test_configure_party()
        code = list(parties.keys())[0]
        partie = parties[code]

        # Sauvegarder l'état de la partie
        saved_dir = os.path.join(BASE_DIR, "partie_sauvegardee")
        filepath = os.path.join(saved_dir, f"saved_state_{code}.json")

        # Appeler la fonction save_state
        state = {
            "modeDeJeu": partie["mode_de_jeu"],
            "joueurs": partie["joueurs"],
            "current_feature_index": partie["current_feature_index"],
            "backlog": partie["backlog"]
        }

        # Sauvegarde dans un fichier JSON
        os.makedirs(saved_dir, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        # Vérification que le fichier est bien généré
        self.assertTrue(os.path.exists(filepath), f"Le fichier {filepath} n'a pas été créé.")
        print(f"Fichier sauvegardé : {filepath}")

        # Charger l'état sauvegardé
        response = self.app.post('/load_state', data={'resume_code': code})
        self.assertEqual(response.status_code, 200, "Échec lors du chargement de l'état.")
        print(f"État chargé avec succès : {parties[code]}")

        # Vérifier que les données chargées correspondent
        self.assertIn(code, parties, "Le code de la partie n'est pas dans les parties chargées.")
        self.assertEqual(parties[code]["mode_de_jeu"], "moyenne", "Le mode de jeu chargé est incorrect.")
        self.assertEqual(parties[code]["joueurs"], partie["joueurs"], "Les joueurs ne correspondent pas.")

    def test_load_state(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Chargement d'une partie sauvegardée.\n\n")
        code = 'TEST123'
        saved_dir = os.path.join(BASE_DIR, "partie_sauvegardee")
        filepath = os.path.join(saved_dir, f"saved_state_{code}.json")

        state = {
            "modeDeJeu": "moyenne",
            "joueurs": ["player1", "player2"],
            "current_feature_index": 0,
            "backlog": [
                {"id": 1, "name": "Feature 1", "description": "Description 1"}
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        response = self.app.post('/load_state', data={
            'resume_code': code
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(code, parties)
        print(f"-> Partie {code} chargée avec succès.")

    def test_submit_player_vote(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Soumission d'un vote.\n\n")
        self.test_configure_party()
        code = list(parties.keys())[0]
        parties[code]['joueurs'].append('player1')
        response = self.app.post('/submit_player_vote', data={
            'vote': '5'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("-> Vote soumis avec succès pour le joueur 'player1'.")


    def test_party_end(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Fin d'une partie.")
        self.test_configure_party()
        code = list(parties.keys())[0]

        # Simuler la fin d'une partie
        parties[code]['current_feature_index'] = len(parties[code]['backlog'])
        response = self.app.get(f'/party_end?code={code}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Partie Termin\xc3\xa9e", response.data)
        print("-> Partie terminée avec succès.")

    def test_chat_message(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTest: Envoi d'un message dans le chat.\n\n")
        self.test_configure_party()
        code = list(parties.keys())[0]
        player_name = 'host_player'

        # Envoyer un message
        response = self.app.post('/send_message', data={
            'message': 'Hello World'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn({"player": player_name, "text": "Hello World"}, parties[code]['chat'])
        print("-> Message 'Hello World' envoyé avec succès par 'host_player'.")

    def tearDown(self):
        print("\n\n----------------------------------------------------------------------")
        print("\t\tTeardown: Nettoyage des fichiers générés.\n\n")
        # Nettoyer les fichiers générés
        saved_dir = os.path.join(BASE_DIR, "partie_sauvegardee")
        results_dir = os.path.join(BASE_DIR, "resultats")

        for folder in [saved_dir, results_dir]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f"Fichier supprimé: {file_path}")
                except Exception as e:
                    print(f"Erreur lors de la suppression du fichier {file_path}: {e}")


if __name__ == '__main__':
    unittest.main()
