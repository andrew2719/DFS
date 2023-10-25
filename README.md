# Distributed File System using Blockchain Technology

## Project Overview

This project aims to create a public blockchain allowing users to store documents on the network. The unique feature is the hybrid consensus mechanism combining Proof of Stake (PoS) and periodic Proof of Work (PoW) to generate coins. It also offers an API interface for organizations to use this network as a decentralized database.

[//]: # (href for the Documentation folder)
[For detailed code details, please refer to the Documentation folder.](Documentation)

## Installation

[//]: # (jus the basic structre the directories of the project)
Directory structure.
```bash
DFS
├── assets
├── Client
├── DFS_main
├── Server
├── .
├── .
├── .
├── requirements.txt
└── README.md
```


To install the requirements.txt use the following command:

```bash
pip install -r requirements.txt
```
Be in the DFS directory and run the following commands

To Run the server

```bash
python -m DFS_main.main
```

To Run the client

```bash
python -m Client.Client
```



## Key Features

- **Hybrid Consensus Mechanism**: Utilizing both PoS and periodic PoW to ensure network security and reward participants.
- **File Distribution**: Files are split into chunks and distributed across nodes, ensuring redundancy and availability.
- **Data Verification**: Using SHA-256 hashes for data integrity checks.
- **Node Communication**: Nodes communicate for data storage, retrieval, and consensus tasks.
- **Erasure Coding**: Planned implementation to handle node downtime and ensure data redundancy.

## Security Considerations

- **Sybil Attacks**: Risks of malicious nodes trying to gain a disproportionate influence on the network.
  - *Potential Solution*: Implementing Proof of Replication and Proof of SpaceTime, combined with economic incentives and node validation.
  
- **Data Tampering**: The integrity of data chunks is verified using SHA-256 hashes. 

- **Node Behavior**: Periodic checks ensure nodes retain the data they claim to, reducing the risk of malicious behavior.

## Future Enhancements

- **Erasure Coding**: To ensure data is retrievable even if some nodes go offline.
- **Consensus Mechanism Refinement**: Further study and refinement of the PoS and PoW mechanisms.
- **API Extensions**: Expanding the API offerings to cater to diverse organizational needs.

## Positive Aspects

- **Decentralization**: Ensuring no single point of failure.
- **Data Redundancy**: By distributing file chunks across nodes.
- **Security**: Through cryptographic mechanisms and consensus protocols.

## Negative Aspects
- **Scalability**: Scaling might be issue when the network grows.