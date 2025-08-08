from flask import Blueprint, render_template, request
from app.db import get_db_connection
from psycopg2.extras import RealDictCursor

web = Blueprint('web', __name__)


@web.route('/')
def daily_matches():
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
        cursor.execute("""
            SELECT match_id, date, home_team, away_team
            FROM matches
        """)

    rows = cursor.fetchall()
    conn.close()

    match_list = [
        {
            'id': row['match_id'],
            'date': row['date'],
            'home_team': row['home_team'],
            'away_team': row['away_team']
        }
        for row in rows
    ]

    return render_template('daily_matches.html', daily_matches=match_list, team_filter=team_filter)


@web.route('/match/<int:id>')
def match(id):
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
        return "Match not found"

    match_data = {
        'date':       match_row['date'],
        'home_team':  match_row['home_team'],
        'away_team':  match_row['away_team'],
        'home_goals': match_row['home_goals'],
        'away_goals': match_row['away_goals'],
    }

    cursor.execute("""
        SELECT
            shots_on_goal_home, shots_off_goal_home, total_shots_home, blocked_shots_home,
            shots_insidebox_home, shots_outsidebox_home, fouls_home, corner_kicks_home,
            offsides_home, ball_possession_home, yellow_cards_home, red_cards_home,
            goalkeeper_saves_home, total_passes_home, passes_accurate_home,
            "passes_%%_home" AS passes_percent_home, expected_goals_home,

            shots_on_goal_away, shots_off_goal_away, total_shots_away, blocked_shots_away,
            shots_insidebox_away, shots_outsidebox_away, fouls_away, corner_kicks_away,
            offsides_away, ball_possession_away, yellow_cards_away, red_cards_away,
            goalkeeper_saves_away, total_passes_away, passes_accurate_away,
            "passes_%%_away" AS passes_percent_away, expected_goals_away
        FROM match_stats
        WHERE match_id = %s
    """, (id,))

    stats_row = cursor.fetchone()
    conn.close()

    if not stats_row:
        match_stats = None
    else:
        match_stats = dict(stats_row)

    return render_template('match_details.html', match=match_data, stats=match_stats)


@web.route('/teams')
def list_of_teams():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT team_id, name, logo FROM teams")
    rows = cursor.fetchall()
    conn.close()

    teams = [{'id': row['team_id'], 'name': row['name'], 'logo': row['logo']} for row in rows]

    return render_template('list_of_teams.html', teams=teams)


@web.route('/team/<int:id>')
def info_team(id):
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

    return render_template('team_info.html', team=team)


@web.route('/team/players/<int:id>')
def players(id):
    name_filter = request.args.get('name', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if name_filter:
        cursor.execute("""
            SELECT name, age, position, nationality, appearances, goals, assists, passes
            FROM players
            WHERE team_id = %s AND name ILIKE %s
        """, (id, f'%{name_filter}%'))
    else:
        cursor.execute("""
            SELECT name, age, position, nationality, appearances, goals, assists, passes
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

    return render_template('team_players.html', players=players, team_id=id, players_filter=name_filter)