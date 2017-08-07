# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

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
