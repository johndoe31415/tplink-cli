# tplink-cli
This is *WORK IN PROGRESS*. It currently does not function.

This is suppsed to be a command line interface for TP-LINK smart switches for
the home market. They are managed via a proprietary UDP-based protocol that is
encrypted with a hardcoded RC4 key. I've done substantial reverse engineering
work back in 2017 to figure out what the datagrams do, but right now it is not
implemented to actually perform any useful commands via the CLI.

## TCPDump facility
To ease debugging, tplink-cli can interface directly with tcpdump PCAP files:

```
$ tcpdump -lnX -r tplink.pcapng 'udp and ((port 29809) or (port 29808))' | ./tplink.py tcpdump
```

or directly dump live traffic:

```
# tcpdump -lnX -i eth0 'udp and ((port 29809) or (port 29808))' | ./tplink.py tcpdump
```

## License
GNU GPL-3
