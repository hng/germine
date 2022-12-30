# Germine

A gemini application that displays calendar events from an URL to an .ics file. Besides listing the events a simple search can be used (searching summary and location fields).

Developed with the great [jetforce](https://github.com/michael-lazar/jetforce) gemini server framework. Not really optimised atm but functional.

## Configuration

The following ENV variables are used to configure Germine:

`GERMINE_HOST`: The server's host should be set to the local socket that you want to bind to, see [jetforce documentation](https://github.com/michael-lazar/jetforce#usage) (default: `127.0.0.1`)

`GERMINE_HOSTNAME`: The server's hostname should be set to the DNS name that you expect to receive traffic from, see [jetforce documentation](https://github.com/michael-lazar/jetforce#usage) (default: `localhost`)

`GERMINE_CAL_URL`: HTTP(S) URL to an .ics file

`GERMINE_DATEFORMAT_DAY`: dateformat string used for day headers (default: `%a, %d.%m.%y`)

`GERMINE_DATEFORMAT_EVENT`: dateformat string used for event headers (default: `%H:%Mh`)

`GERMINE_SEARCH_INPUT_MESSAGE`: string displayed when opening search input (default: "Search query (searches in event summary and location)")

### Templates

Templates for the header and the additional information displayed when searching can be found in the `templates/` folder. Overwrite them with your own content.
