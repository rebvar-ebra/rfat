# RFat - Raft-based Fault-Tolerant Key-Value Store

RFat is a distributed, consensus-based key-value store implemented in Python, inspired by the Raft consensus algorithm. It provides a reliable way to store and manage key-value pairs across a cluster of nodes, ensuring consistency even in the presence of node failures.

## 🚀 Features

- **Distributed Consensus**: Implements core Raft concepts including leader election, heartbeats, and log replication.
- **Fault Tolerance**: Maintains system availability and data consistency as long as a majority of nodes are operational.
- **Client Redirection**: Clients can connect to any node in the cluster and are automatically redirected to the current leader for write operations.
- **Interactive Client**: A user-friendly CLI client for interacting with the key-value store.
- **Persistence**: Nodes log operations to local files for recovery upon restart.

## 🛠 Architecture

RFat follows the Raft architecture where nodes can be in one of three states: **Follower**, **Candidate**, or **Leader**.

1.  **Leader Election**: If a follower doesn't hear from a leader within a randomized timeout, it becomes a candidate and starts an election.
2.  **Heartbeats**: The leader sends periodic heartbeats to all followers to maintain authority and reset their election timers.
3.  **Log Replication**: All write operations (set, delete) are sent to the leader, which replicates them to the followers before committing and executing them.

## 📋 Prerequisites

- Python 3.x

## 🏁 Getting Started

### 1. Configure the Cluster

The cluster configuration is managed via `server_registry.txt`. Each line should contain the server name, host (usually `localhost`), and port.

Example `server_registry.txt`:
```text
S1 localhost 10000
S2 localhost 10001
S3 localhost 10002
```

### 2. Start Server Nodes

Open separate terminal windows for each node and run:

```bash
# Start Node S1
python3 start_server.py S1 10000

# Start Node S2
python3 start_server.py S2 10001

# Start Node S3
python3 start_server.py S3 10002
```

### 3. Start the Client

Connect the client to any of the running nodes:

```bash
python3 start_client.py 10000
```

## ⌨️ Usage

Once the client is connected, you can use the following commands:

| Command | Description |
| :--- | :--- |
| `set <key> <value>` | Store a value for a given key. |
| `get <key>` | Retrieve the value for a given key. |
| `delete <key>` | Remove a key-value pair. |
| `show` | Display the entire key-value store content. |
| `show_log` | Display the operation log of the connected node. |
| `youre_the_leader` | Force a node to become the leader (for testing/debugging). |
| `quit` | Exit the client. |

## 📁 Project Structure

- `server.py`: The core server logic implementing Raft states and RPC handlers.
- `node.py`: The interactive client implementation.
- `key_value_operation.py`: The underlying key-value store and logging logic.
- `config.py`: Utilities for reading cluster configuration.
- `message_pass.py`: Helper functions for socket communication.
- `start_server.py` / `start_client.py`: Entry point scripts for launching nodes and the client.

## ⚖️ License

This project is open-source and available under the [MIT License](LICENSE).
