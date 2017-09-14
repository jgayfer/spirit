CREATE TABLE guilds (
	guild_id BIGINT NOT NULL,
	prefix VARCHAR(5) NOT NULL DEFAULT '!',
	clear_spam BOOLEAN NOT NULL DEFAULT 0,
	event_role_id DECIMAL(20),
	PRIMARY KEY(guild_id)
);

CREATE TABLE users (
	username VARCHAR(50) NOT NULL,
	platform INT,
	membership_id DECIMAL(20),
	PRIMARY KEY (username)
);

CREATE TABLE events (
	guild_id BIGINT NOT NULL,
	start_time DATETIME NOT NULL,
	timezone VARCHAR(6) NOT NULL,
	title VARCHAR(256) NOT NULL,
	description VARCHAR(1000),
	max_members INT NOT NULL DEFAULT 0,
	username VARCHAR(50),
	PRIMARY KEY (guild_id, title),
	FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
		ON DELETE CASCADE
);

CREATE TABLE user_event (
	username VARCHAR(50) NOT NULL,
	guild_id BIGINT NOT NULL,
	title VARCHAR(256) NOT NULL,
	attending BOOLEAN NOT NULL,
	last_updated DATETIME NOT NULL,
	PRIMARY KEY (username, guild_id, title),
	FOREIGN KEY (guild_id, title) REFERENCES events(guild_id, title)
		ON DELETE CASCADE,
	FOREIGN KEY (username) REFERENCES users(username)
	  ON DELETE CASCADE
);

CREATE TABLE roster (
	username VARCHAR(50) NOT NULL,
	guild_id BIGINT NOT NULL,
	role VARCHAR(10),
	timezone VARCHAR(6),
	PRIMARY KEY (username, guild_id),
	FOREIGN KEY (username) REFERENCES users(username)
		ON DELETE CASCADE,
	FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
		ON DELETE CASCADE
);
