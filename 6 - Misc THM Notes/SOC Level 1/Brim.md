Brim is an open-source desktop application that processes pcap files and logs files, with a primary focus on providing search and analytics. It uses the Zeek log processing format. It also supports Zeek signatures and Suricata Rules for detection.

It can handle two types of data as an input;

- Packet Capture Files: Pcap files created with tcpdump, tshark and Wireshark like applications.
- Log Files: Structured log files like Zeek logs.

Brim is built on open-source platforms:

- **Zeek:** Log generating engine.
- **Zed Language:** Log querying language that allows performing keywoırd searches with filters and pipelines.
- **ZNG Data Format:** Data storage format that supports saving data streams.
- **Electron and React:** Cross-platform UI.


![](/assets/images/Brim/Screenshot%202024-12-29%20at%203.13.45%20PM.png)


It comes with Premade queries which perform different tasks on the files split out from the pcap. 

The `Unique Network Connections and Transferred Data` query is:
`_path=="conn" | cut id.orig_h, id.resp_p, id.resp_h | sort | uniq`
- Uses the connections log
- Grabs the client IP, the server Port and IP, and then filters for only the unique connections


