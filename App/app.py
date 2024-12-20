import os
import json
import random
import string
import time
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "api_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOTE_DURATION = 60

def load_backlog(filename: str):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Le fichier {filepath} n'existe pas.")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

global_backlog = load_backlog('backlog.json')

parties = {}

def generate_party_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        mode_de_jeu = request.form.get('mode_de_jeu')

        nb_joueurs = int(request.form.get('nombre_joueurs', 0))
        creator_pseudo = request.form.get('player_0')
        if not creator_pseudo:
            return "Vous devez entrer au moins un pseudo pour le créateur."

        party_backlog = [dict(feature) for feature in global_backlog]
        code = generate_party_code()
        parties[code] = {
            "mode_de_jeu": mode_de_jeu,
            "joueurs": [creator_pseudo],
            "nombre_joueurs_max": nb_joueurs,
            "current_feature_index": 0,
            "round": 1,
            "backlog": party_backlog,
            "votes": {},
            "chat": [],
            "end_time": time.time() + VOTE_DURATION
        }

        session['party_code'] = code
        session['player_name'] = creator_pseudo
        return redirect(url_for('player_vote'))
    return render_template('configure.html')


@app.route('/join', methods=['GET'])
def join():
    return render_template('join.html')

@app.route('/join_party', methods=['POST'])
def join_party():
    code = request.form.get('party_code')
    pseudo = request.form.get('player_name')
    if code in parties:
        partie = parties[code]
        if pseudo in partie['joueurs']:
            session['party_code'] = code
            session['player_name'] = pseudo
            return redirect(url_for('player_vote'))
        else:
            if len(partie['joueurs']) >= partie['nombre_joueurs_max']:
                return "La partie a déjà atteint le nombre maximum de joueurs."
            partie['joueurs'].append(pseudo)
            session['party_code'] = code
            session['player_name'] = pseudo
            return redirect(url_for('player_vote'))
    else:
        return "Code de partie invalide. <a href='{}'>Retour</a>".format(url_for('join'))

@app.route('/resume', methods=['GET'])
def resume():
    return render_template('resume.html')

@app.route('/load_state', methods=['POST'])
def load_state():
    code = request.form.get('resume_code')
    saved_dir = os.path.join(BASE_DIR, "partie_sauvegardee")
    filepath = os.path.join(saved_dir, f"saved_state_{code}.json")

    if not os.path.exists(filepath):
        return f"Aucun état sauvegardé pour le code {code}."

    with open(filepath, 'r', encoding='utf-8') as f:
        state = json.load(f)

    parties[code] = {
        "mode_de_jeu": state["modeDeJeu"],
        "joueurs": state["joueurs"],
        "nombre_joueurs_max": len(state["joueurs"]),
        "current_feature_index": state["current_feature_index"],
        "round": 1,
        "backlog": state["backlog"],
        "votes": {},
        "chat": [],
        "end_time": time.time() + VOTE_DURATION
    }

    return f"Partie chargée. Code : {code}. <a href='{url_for('join')}'>Rejoindre la partie</a>"

@app.route('/player_vote', methods=['GET'])
def player_vote():
    code = session.get('party_code')
    player = session.get('player_name')
    if not code or code not in parties or player not in parties[code]['joueurs']:
        return "Vous n'êtes pas dans une partie ou partie invalide."

    partie = parties[code]
    current_index = partie['current_feature_index']

    if partie.get('needs_refresh', False):
        partie['needs_refresh'] = False

    if current_index >= len(partie['backlog']):
        return redirect(url_for('party_end', code=code))

    feature = partie['backlog'][current_index]
    cartes = ["0","1","2","3","5","8","13","20","40","100","cafe","interrogation"]
    end_time = int(partie['end_time'])
    chat = partie.get('chat', [])

    if player in partie['votes']:
        all_voted = (len(partie['votes']) == len(partie['joueurs']))
        return render_template('player_wait.html', all_voted=all_voted, code=code)
    else:
        return render_template('player_vote.html', feature=feature, cartes=cartes, code=code, player=player, end_time=end_time, chat=chat)

@app.route('/status')
def status():
    code = request.args.get('code')
    if code not in parties:
        return {"error": "Partie introuvable"}, 404

    partie = parties[code]
    current_index = partie['current_feature_index']
    all_voted = (len(partie['votes']) == len(partie['joueurs']))
    finished = (current_index >= len(partie['backlog']))
    needs_refresh = partie.get('needs_refresh', False)

    partie['needs_refresh'] = False

    return {
        "all_voted": all_voted,
        "finished": finished,
        "chat": partie['chat'],
        "needs_refresh": needs_refresh
    }


@app.route('/send_message', methods=['POST'])
def send_message():
    code = session.get('party_code')
    player = session.get('player_name')
    if not code or code not in parties or player not in parties[code]['joueurs']:
        return "Partie ou joueur invalide."
    message = request.form.get('message')
    if message:
        parties[code]['chat'].append({"player": player, "text": message})
    return redirect(url_for('player_vote'))


@app.route('/submit_player_vote', methods=['POST'])
def submit_player_vote():
    code = session.get('party_code')
    player = session.get('player_name')

    if not code or code not in parties or player not in parties[code]['joueurs']:
        return "Partie ou joueur invalide."

    partie = parties[code]
    vote = request.form.get('vote')
    now = time.time()

    if now > partie['end_time']:
        # Si le temps est écoulé, attribuer le vote par défaut "interrogation"
        vote = "interrogation"

    partie['votes'][player] = vote

    # Vérifier si tous les joueurs ont voté
    if len(partie['votes']) == len(partie['joueurs']):
        round_number = partie['round']
        current_index = partie['current_feature_index']
        chosen_values = list(partie['votes'].values())

        # Vérifiez si le mode est "unanimité"
        if partie["mode_de_jeu"] == "unanimite":
            if len(set(chosen_values)) == 1:  # Tous les votes sont identiques
                partie['backlog'][current_index]['estimatedDifficulty'] = chosen_values[0]
                partie['current_feature_index'] += 1
                partie['round'] = 1
                partie['votes'] = {}
                if partie['current_feature_index'] < len(partie['backlog']):
                    partie['end_time'] = time.time() + VOTE_DURATION
            else:
                # Pas d'unanimité, redémarrer le vote
                partie['round'] = 2
                partie['votes'] = {}
                partie['end_time'] = time.time() + VOTE_DURATION
                partie['needs_refresh'] = True
            return redirect(url_for('player_vote'))

        # Fonction pour sauvegarder l'état de la partie
        def save_state(code, partie):
            saved_dir = os.path.join(BASE_DIR, "partie_sauvegardee")
            os.makedirs(saved_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas

            filepath = os.path.join(saved_dir, f"saved_state_{code}.json")
            state = {
                "modeDeJeu": partie["mode_de_jeu"],
                "joueurs": partie["joueurs"],
                "current_feature_index": partie["current_feature_index"],
                "backlog": partie["backlog"]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)



        if round_number == 1:
            unique_values = set(chosen_values)
            if partie["mode_de_jeu"] == "unanimite":
                if len(set(chosen_values)) == 1:  # Tous les votes sont identiques
                    val = chosen_values[0]
                    partie['backlog'][current_index]['estimatedDifficulty'] = val  # Correction
                    partie['current_feature_index'] += 1
                    partie['round'] = 1
                    partie['votes'] = {}
                    if partie['current_feature_index'] < len(partie['backlog']):
                        partie['end_time'] = time.time() + VOTE_DURATION
                else:
                    # Pas d'unanimité -> Réinitialiser les votes
                    partie['round'] = 2
                    partie['votes'] = {}
                    partie['end_time'] = time.time() + VOTE_DURATION
                    partie['needs_refresh'] = True
                return redirect(url_for('player_vote'))


            elif len(unique_values) == 1 and "cafe" not in unique_values:
                # Tous les joueurs sont unanimes
                val = unique_values.pop()
                partie['backlog'][current_index]['estimatedDifficulty'] = val
                partie['current_feature_index'] += 1
                partie['round'] = 1
                partie['votes'] = {}
                if partie['current_feature_index'] < len(partie['backlog']):
                    partie['end_time'] = time.time() + VOTE_DURATION
            elif len(unique_values) == 1 and "cafe" in unique_values:
                save_state(code, partie)  # Sauvegarde l'état de la partie
                return "État sauvegardé après café. Vous pouvez reprendre plus tard."
            else:
                # Pas unanimité, passage au second tour
                partie['round'] = 2
                partie['votes'] = {}
                partie['end_time'] = time.time() + VOTE_DURATION
                partie['needs_refresh'] = True
        else:
            # Second tour de vote
            if all(v == "cafe" for v in chosen_values):
                save_state(code, partie)
                return "État sauvegardé après café. Vous pouvez reprendre plus tard."

            numeric_votes = [int(v) for v in chosen_values if v.isdigit()]
            mode_de_jeu = partie['mode_de_jeu']

            if not numeric_votes:
                partie['backlog'][current_index]['estimatedDifficulty'] = None
            else:
                if mode_de_jeu == "moyenne":
                    estimate = round(sum(numeric_votes) / len(numeric_votes))
                elif mode_de_jeu == "mediane":
                    numeric_votes.sort()
                    mid = len(numeric_votes) // 2
                    if len(numeric_votes) % 2 == 1:
                        estimate = numeric_votes[mid]
                    else:
                        estimate = round((numeric_votes[mid - 1] + numeric_votes[mid]) / 2)
                elif mode_de_jeu == "majorite":
                    from collections import Counter
                    freq = Counter(numeric_votes)
                    max_count = max(freq.values())
                    candidates = [k for k, v in freq.items() if v == max_count]
                    estimate = min(candidates)

                partie['backlog'][current_index]['estimatedDifficulty'] = estimate

            partie['current_feature_index'] += 1
            partie['round'] = 1
            partie['votes'] = {}
            if partie['current_feature_index'] < len(partie['backlog']):
                partie['end_time'] = time.time() + VOTE_DURATION

    return redirect(url_for('player_vote'))


@app.route('/party_end')
def party_end():
    code = request.args.get('code', session.get('party_code'))
    if code not in parties:
        return "Partie introuvable."

    partie = parties[code]
    backlog = partie['backlog']

    # Créez le dossier "resultats" s'il n'existe pas
    results_dir = os.path.join(BASE_DIR, "resultats")
    os.makedirs(results_dir, exist_ok=True)

    # Sauvegarde des résultats dans le dossier "resultats"
    results = {
        "code_partie": code,
        "mode_de_jeu": partie['mode_de_jeu'],
        "joueurs": partie['joueurs'],
        "fonctionnalites": backlog
    }

    results_filepath = os.path.join(results_dir, f"resultats_{code}.json")
    with open(results_filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return render_template('party_end.html', backlog=backlog, results_file=f"resultats/resultats_{code}.json")

if __name__ == "__main__":
    app.run(debug=True)