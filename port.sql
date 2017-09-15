insert into users (user_id, platform, membership_id) select user_id, platform, membership_id from users_old;

insert into guilds (guild_id, prefix, clear_spam) select guild_id, prefix, clear_spam from guilds_old;

insert into events (guild_id, start_time, timezone, title, description, max_members) select guild_id, start_time, timezone, title, description, max_members from event_old;

insert into roster (user_id, guild_id, role, timezone) select user_id, guild_id, role, timezone from roster_old;

insert into user_event (user_id, guild_id, title, attending, last_updated) select user_id, guild_id, title, attending, last_updated from user_event_old;

drop table user_event_old;
drop table roster_old;
drop table event_old;
drop table users_old;
drop table guilds_old;
