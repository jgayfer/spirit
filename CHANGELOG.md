# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
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
