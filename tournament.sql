-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

\i tournament.sql

DROP DATABASE tournament IF EXISTS;

CREATE TABLE PLAYERS(
	id SERIAL PRIMARY KEY,
	name VARCHAR(100)
	);


CREATE TABLE MATCHES(
	id SERIAL PRIMARY KEY,
	p1_id int REFERENCES PLAYERS(id) on DELETE CASCADE,
	p2_id int REFERENCES PLAYERS(id) on DELETE CASCADE,
	win int,
	loss int
	);


CREATE TABLE STATS(
	id int REFERENCES PLAYERS(id) on DELETE CASCADE,
	player_name VARCHAR(100),
	win int,
	loss int,
	no_match int
	);
