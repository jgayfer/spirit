CREATE TABLE users (
	username VARCHAR(50) NOT NULL,
	role VARCHAR(10),
	PRIMARY KEY (username)
);

CREATE TABLE servers (
	server_id VARCHAR(40) NOT NULL,
	name VARCHAR(40) NOT NULL,
	PRIMARY KEY (server_id)
);

CREATE TABLE events (
	event_id int NOT NULL AUTO_INCREMENT,
	server_id VARCHAR(40) NOT NULL,
	start_time DATETIME NOT NULL,
	title VARCHAR(256) NOT NULL,
	description VARCHAR(500),
	PRIMARY KEY (event_id),
	FOREIGN KEY (server_id) REFERENCES servers(server_id)
		ON DELETE CASCADE
);

CREATE TABLE user_event (
	username VARCHAR(50) NOT NULL,
	event_id int NOT NULL,
	attending BOOLEAN,
	PRIMARY KEY (username, event_id),
	FOREIGN KEY (username) REFERENCES users(username)
		ON DELETE CASCADE,
	FOREIGN KEY (event_id) REFERENCES events(event_id)
		ON DELETE CASCADE
);

CREATE TABLE user_server (
	username VARCHAR(50) NOT NULL,
	server_id VARCHAR(40) NOT NULL,
	PRIMARY KEY (username, server_id),
	FOREIGN KEY (username) REFERENCES users(username)
		ON DELETE CASCADE,
	FOREIGN KEY (server_id) REFERENCES servers(server_id)
		ON DELETE CASCADE
);
