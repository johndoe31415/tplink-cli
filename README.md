# tplink-cli
This is *WORK IN PROGRESS*. It currently does not function.

This is suppsed to be a command line interface for TP-LINK smart switches for
the home market. They are managed via a proprietary UDP-based protocol that is
encrypted with a hardcoded RC4 key. I've done substantial reverse engineering
work back in 2017 to figure out what the datagrams do, but right now it is not
implemented to actually perform any useful commands via the CLI.

## License
GNU GPL-3
