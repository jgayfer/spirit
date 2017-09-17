# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- Fixed an issue where adding an emoji in a private/group message that Spirit is aware of
could cause issues.

## [1.2.0]
### Added
- Manage Server members can now define the lowest role that can create events
- Event creator/organizer is now displayed in each event message
### Changed
- By default, everyone can create events. Manage Server members and event creators are the only ones who can delete events.
- Roster and settings are now group commands. The old command are still there, but now they must
be prefixed by either `roster` or `settings`. For more information, check out the new `help` message
- Message prompts will now time out after a minute if the bot doesn't get a response
- Previously admin only commands now require the Manage Server permission instead
### Fixed
- Nightfall command would be unresponsive if Bungie.net couldn't be reached
- Registering would fail if there were two account names with different capitalization
- Changing your username would result in duplicate entries in the roster

## [1.1.2] - 2017-09-09
### Fixed
- Invalid Bungie account names would cause the register command to be unresponsive

## [1.1.1] - 2017-09-09
### Fixed
- Help message couldn't be invoked by mentioning the bot outside of a private message
- Displaying a user's nickname in the roster would sometimes fail
- Fix crashing issue related to discord.py

## [1.1.0] - 2017-09-08
### Added
- Add 'register' command. Allows users to register their Destiny 2 account with the bot.
- Add 'nightfall' command. This displays information about the weekly nightfall strike.
- Add 'loadout' command. This displays your last played character's loadout.
- Add raid release date for consoles to the countdown command.
- The roster will now display a member's nickname instead of their username if a nickname is set.
- Add error message when invoking a command that a user doesn't have permissions to invoke.
### Changed
- When the bot restarts, event messages are no longer resent. This means you won't get a notification
every time the bot is restarted.

## [1.0.3] - 2017-08-30
### Fixed
- Users could not invoke commands if they added the bot to their server while the bot was offline, and then it came back online

## [1.0.2] - 2017-08-27
### Fixed
- Event creation would fail if no description was given

## [1.0.1] - 2017-08-26
### Fixed
- Countdown command was displaying incorrect values

## [1.0.0] - 2017-08-25
### Added
- Command spam cleanup is now optional. It can be turned on/off with the 'togglecleanup' command
- Bot owner can now respond to feedback messages via a command
### Changed
- Moved to version 1.0.0a of Discord.py (essentially a full rewrite of the bot)
- Event creation now happens in a DM to reduce spam
- Updated feedback message to provide bot owner with more context
### Fixed
- Fix typos

## [0.6.0] - 2017-08-22
### Added
- Commands can now be invoked by mentioning the bot
- Welcome message is now sent to server owner when bot joins a server
- Help command now lists individual subcommands of a base command if there are any
### Fixed
- Fix typos

## [0.5.2] - 2017-08-18
### Fixed
- Bug where setting your timezone before assigning a role wouldn't work

## [0.5.1] - 2017-08-12
### Fixed
- Countdown command was displaying incorrect values

## [0.5.0] - 2017-08-12
### Added
- New command 'countdown' displays time until upcoming Destiny 2 releases
- Help command now supports individual commands and subcommands (Eg. '!help event')
- Command help messages are now much more descriptive
- Error message now displays when an invalid command is invoked, or an argument is missing
### Changed
- Help command now displays command arguments (both required and optional)
- Changed the name of certain commands to be more descriptive
### Fixed
- Internal exception that occurred when users added a reaction to a non embed message

## [0.4.0] - 2017-08-08
### Added
- Users can now add their timezone to the roster with the new 'timezone' command
- The roster now displays the server name in its title
### Changed
- Changed the name of the 'setprefix' command to 'prefix'

## [0.3.0] - 2017-08-07
### Added
- A maximum number of attendees can be specified for an event
- A 'standby' section has been added to events that have more attendees than the event permits
### Changed
- Events are now sorted in the events channel by their start time
- Event attendees are now sorted by when they accepted the invitation

## [0.2.0] - 2017-08-02
### Added
- Custom command prefixes
- Command to send feedback to the developer
- Message to indicate when there are no upcoming events
### Changed
- Events are now deleted with a reaction instead of a command
- User and bot spam messages are now deleted much faster
### Fixed
- Issue that prevented emojis being included in event title/description

## [0.1.1] - 2017-07-26
### Added
- Title to help message
### Changed
- Spirit now listens for follow up command messages only on the channel in which the command was invoked
### Fixed
- Fix message cleanup bug that occurred when a command was invoked while the bot was waiting for a follow up message

## [0.1.0] - 2017-07-26
### Added
- Events
  - Admins can create and delete events with the `!event create` and `!event delete` commands
  - Users can view and RSVP to upcoming events by reacting with emojis
- Roster
  - Users can indicate which class they plan on playing in Destiny 2 with the `!role` command
  - Users can view which classes other members are planning to play with the `!roster` command
