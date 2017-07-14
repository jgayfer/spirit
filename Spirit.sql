CREATE TABLE users (
	user varchar(30) NOT NULL,
	role varchar(10),
	server_id varchar(30) NOT NULL,
	PRIMARY KEY (user, server_id)
	);
	
	
