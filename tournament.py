#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("TRUNCATE matches CASCADE;")
    c.execute("ALTER sequence matches_id_seq RESTART WITH 1;")
    conn.commit()
    c.execute("SELECT * FROM stats;")
    if bool(c.rowcount):
        c.execute("SELECT * FROM players")
        rows = c.fetchall()
        for row in rows:
            c.execute("UPDATE stats set win = (%s), loss = (%s), no_match = (%s) where id = (%s) and player_name = (%s)", (0,0,0,row[0],row[1],))
        conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("TRUNCATE players CASCADE;")
    c.execute("ALTER sequence players_id_seq RESTART WITH 1;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT count(*) as num FROM players;")
    count = c.fetchone()[0]
    conn.close()
    return count



def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players(name) VALUES((%s));",(name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM stats;")
    if not bool(c.rowcount):
        c.execute("SELECT * FROM players;")
        rows = c.fetchall()
        for row in rows:
            c.execute("INSERT INTO stats(id,win,loss,player_name,no_match) VALUES ((%s),0,0,(%s),0);",(row[0],row[1],))
        conn.commit()
    c.execute("SELECT id,player_name,win,no_match FROM stats ORDER By win DESC;")
    rows = c.fetchall()
    record = []
    for row in rows:
        record.append(row)
    return record


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO matches(p1_id,p2_id,win,loss) VALUES((%s),(%s),(%s),(%s))",(winner,loser,winner,loser))
    c.execute("UPDATE stats set win = win + 1, no_match = no_match + 1 WHERE id = (%s);",(winner,))
    c.execute("UPDATE stats set loss = loss + 1, no_match = no_match + 1 WHERE id = (%s);",(loser,))
    conn.commit()
    conn.close()



def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    c = conn.cursor()
# handle empty matches condition
    c.execute("SELECT * FROM matches;")
    if not bool(c.rowcount):
        c.execute("SELECT * FROM players;")
        rows = c.fetchall()
        p_list, id_list, player_name_list = [], [], []
        for row in rows:
            id_list.append(row[0])
            player_name_list.append(row[1])
        for i in xrange(0, len(id_list), 2):
            tup = (id_list[i],player_name_list[i],id_list[i+1],player_name_list[i+1])
            p_list.append(tup)
        return p_list
    else:
        c.execute("SELECT id, player_name FROM stats WHERE win > loss;")
#  First fetch all winners and pair them
        rows = c.fetchall()
        id_list, p_name,players_list = [], [], [],
        for row in rows:
            id_list.append(row[0])
            p_name.append(row[1])
        for i in range(0,len(p_name),2):
            t = (id_list[i],p_name[i],id_list[i+1],p_name[i+1])
            players_list.append(t)
        c.execute("SELECT id, player_name FROM stats WHERE loss > win;")
# Fetch all the losers and pair them
        rows = c.fetchall()
        id_list, p_name,= [], [],
        for row in rows:
            id_list.append(row[0])
            p_name.append(row[1])
        for i in range(0,len(p_name),2):
            t = (id_list[i],p_name[i],id_list[i+1],p_name[i+1])
            players_list.append(t)
        return players_list
