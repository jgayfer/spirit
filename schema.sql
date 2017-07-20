CREATE TABLE users (
	username VARCHAR(50) NOT NULL,
	PRIMARY KEY (username)
);

CREATE TABLE events (
	server_id VARCHAR(40) NOT NULL,
	start_time DATETIME NOT NULL,
	time_zone VARCHAR(5) NOT NULL,
	title VARCHAR(256) NOT NULL,
	description VARCHAR(1000),
	event_id int NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (event_id)
);

CREATE TABLE user_event (
	username VARCHAR(50) NOT NULL,
	event_id int NOT NULL,
	attending BOOLEAN NOT NULL,
	PRIMARY KEY (username, event_id),
	FOREIGN KEY (username) REFERENCES users(username)
		ON DELETE CASCADE,
	FOREIGN KEY (event_id) REFERENCES events(event_id)
		ON DELETE CASCADE
);

CREATE TABLE roles (
	username VARCHAR(50) NOT NULL,
	server_id VARCHAR(40) NOT NULL,
	role VARCHAR(10) NOT NULL,
	PRIMARY KEY (username, server_id),
	FOREIGN KEY (username) REFERENCES users(username)
		ON DELETE CASCADE
);
