from flask import Blueprint, request, redirect
from app.db import get_db_connection

http_m = Blueprint('http_m', __name__, url_prefix='/http_m')

@http_m.route('/add_match', methods=['POST'])
def add_match():
    if request.is_json:
        data = request.get_json()
        home_team = data.get('home_team', '').strip()
        away_team = data.get('away_team', '').strip()
        date = data.get('date', '').strip()
        league = data.get('league', '').strip()
        home_goals = data.get('home_goals', 0)
        away_goals = data.get('away_goals', 0)
    else:
        home_team = request.form.get('home_team', '').strip()
        away_team = request.form.get('away_team', '').strip()
        date = request.form.get('date', '').strip()
        league = request.form.get('league', '').strip()
        home_goals = request.form.get('home_goals', 0)
        away_goals = request.form.get('away_goals', 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO matches (date, league, home_team, away_team, home_goals, away_goals)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, league, home_team, away_team, home_goals, away_goals))
    conn.commit()
    conn.close()

    return redirect('/http_m/added')


@http_m.route('/match/<int:id>', methods=['PATCH'])
def edit_match(id):
    if request.is_json:
        data = request.get_json()
        date = data.get('date', '').strip()
        home_goals = data.get('home_goals', '').strip()
        away_goals = data.get('away_goals', '').strip()
    else:
        date = request.form.get('date', '').strip()
        home_goals = request.form.get('home_goals', '').strip()
        away_goals = request.form.get('away_goals', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE matches
        SET date = ?, home_goals = ?, away_goals = ?
        WHERE match_id = ?
    """, (date, home_goals, away_goals, id))
    conn.commit()
    conn.close()

    return redirect('/http_m/edited')


@http_m.route('/match/<int:id>', methods=['DELETE'])
def delete_match(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches WHERE match_id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect('/http_m/deleted')


@http_m.route('/added')
def added():
    return "<h2>Match added successfully!</h2><a href='/add_match'>Add another</a>"

@http_m.route('/edited')
def edited():
    return "<h2>Match edited successfully!</h2><a href='/match/<int:id>'>Edit another</a>"

@http_m.route('/deleted')
def deleted():
    return "<h2>Match deleted successfully!</h2><a href='/match/<int:id>'>Delete another</a>"