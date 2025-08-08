from flask import Blueprint, jsonify, request
from app.db import get_db_connection
from psycopg2.extras import RealDictCursor

api = Blueprint('api', __name__)

@api.route('/matches')
def api_matches():
    team_filter = request.args.get('team', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if team_filter:
        cursor.execute("""
                       SELECT match_id, date, home_team, away_team
                       FROM matches
                       WHERE home_team ILIKE %s OR away_team ILIKE %s
                       """, (f'%{team_filter}%', f'%{team_filter}%'))
    else:
        cursor.execute("SELECT match_id, date, home_team, away_team FROM matches")
    rows = cursor.fetchall()
    conn.close()

    match_list = [
        {
            'id': row['match_id'],
            'date': row['date'],
            'home_team': row['home_team'],
            'away_team': row['away_team'],
        }
        for row in rows
    ]

    return jsonify(match_list)


@api.route('/match/<int:id>')
def api_match(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT f.date, t1.name  AS home_team, t2.name  AS away_team, f.home_goals, f.away_goals
        FROM matches f
        JOIN teams t1 ON f.home_team = t1.name
        JOIN teams t2 ON f.away_team = t2.name
        WHERE f.match_id = %s
    """, (id,))
    match_row = cursor.fetchone()

    if not match_row:
        conn.close()
        return jsonify({'error': 'Match not found'}), 404

    match_data = {
        'date': match_row['date'],
        'home_team': match_row['home_team'],
        'away_team': match_row['away_team'],
        'home_goals': match_row['home_goals'],
        'away_goals': match_row['away_goals']
    }

    cursor.execute("""SELECT * FROM match_stats WHERE match_id = %s""", (id,))
    stats_row = cursor.fetchone()
    conn.close()

    if stats_row:
        stats_dict = dict(stats_row)
        match_data['stats'] = stats_dict
    else:
        match_data['stats'] = None

    return jsonify(match_data)


@api.route('/teams')
def api_teams():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT team_id, name FROM teams")
    rows = cursor.fetchall()
    conn.close()

    teams = [{'id': row['team_id'], 'name': row['name']} for row in rows]

    return jsonify(teams)

@api.route('/team/<int:id>')
def api_team(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
                   SELECT name, country, founded, venue_name, venue_city, capacity, logo
                   FROM teams
                   WHERE team_id = %s
                   """, (id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Team not found"
    else:
        team = {
            'id': id,
            'name': row['name'],
            'country': row['country'],
            'founded': row['founded'],
            'venue_name': row['venue_name'],
            'venue_city': row['venue_city'],
            'capacity': row['capacity'],
            'logo': row['logo']
        }

    return jsonify(team)


@api.route('/team/<int:id>/players')
def api_players(id):
    name_filter = request.args.get('name', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if name_filter:
        cursor.execute("""
            SELECT name,age,position,nationality,appearances,goals,assists,passes
            FROM players
            WHERE team_id = %s
            AND name ILIKE %s
        """, (id, f'%{name_filter}%'))
    else:
        cursor.execute("""
            SELECT name,age,position,nationality,appearances,goals,assists,passes
            FROM players
            WHERE team_id = %s
        """, (id,))

    rows = cursor.fetchall()
    conn.close()

    players = [
        {
            'name': row['name'],
            'age': row['age'],
            'position': row['position'],
            'nationality': row['nationality'],
            'appearances': row['appearances'],
            'goals': row['goals'],
            'assists': row['assists'],
            'passes': row['passes'],
        }
        for row in rows
    ]
    return jsonify(players)


