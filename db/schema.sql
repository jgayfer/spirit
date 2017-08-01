CREATE TABLE servers (
	server_id VARCHAR(40) NOT NULL,
	prefix VARCHAR(5) NOT NULL DEFAULT '!',
	clear_spam BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY(server_id)
);

CREATE TABLE users (
	username VARCHAR(50) NOT NULL,
	server_id VARCHAR(40) NOT NULL,
	role VARCHAR(10),
	PRIMARY KEY (username, server_id),
	FOREIGN KEY (server_id) REFERENCES servers(server_id)
	  ON DELETE CASCADE
);

CREATE TABLE events (
	server_id VARCHAR(40) NOT NULL,
	start_time DATETIME NOT NULL,
	time_zone VARCHAR(5) NOT NULL,
	title VARCHAR(256) NOT NULL,
	description VARCHAR(1000),
	PRIMARY KEY (server_id, title),
	FOREIGN KEY (server_id) REFERENCES servers(server_id)
		ON DELETE CASCADE
);

CREATE TABLE user_event (
	username VARCHAR(50) NOT NULL,
	server_id VARCHAR(40) NOT NULL,
	title VARCHAR(256) NOT NULL,
	attending BOOLEAN NOT NULL,
	PRIMARY KEY (username, server_id, title),
	FOREIGN KEY (server_id, title) REFERENCES events(server_id, title)
		ON DELETE CASCADE,
	FOREIGN KEY (server_id, username) REFERENCES users(server_id, username)
	  ON DELETE CASCADE
);
