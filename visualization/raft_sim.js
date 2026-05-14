const STATES = {
    FOLLOWER: 'follower',
    CANDIDATE: 'candidate',
    LEADER: 'leader',
    DEAD: 'dead'
};

const RPC_TYPES = {
    REQUEST_VOTE: 'request_vote',
    VOTE_RESPONSE: 'vote_response',
    APPEND_ENTRIES: 'append_entries',
    APPEND_RESPONSE: 'append_response'
};

class RaftNode {
    constructor(id, cluster) {
        this.id = id;
        this.cluster = cluster;
        this.state = STATES.FOLLOWER;
        this.term = 0;
        this.votedFor = null;
        this.log = [];
        this.commitIndex = 0;
        this.lastApplied = 0;
        
        // Timer settings (ms)
        this.electionTimeout = this.getRandomTimeout();
        this.electionElapsed = 0;
        this.heartbeatInterval = 1500;
        this.heartbeatElapsed = 0;
        
        // Leader state
        this.nextIndex = {};
        this.matchIndex = {};
        this.votesReceived = new Set();
    }

    getRandomTimeout() {
        return 4000 + Math.random() * 4000;
    }

    update(dt) {
        if (this.state === STATES.DEAD) return;

        if (this.state === STATES.LEADER) {
            this.heartbeatElapsed += dt;
            if (this.heartbeatElapsed >= this.heartbeatInterval) {
                this.sendHeartbeats();
                this.heartbeatElapsed = 0;
            }
        } else {
            this.electionElapsed += dt;
            if (this.electionElapsed >= this.electionTimeout) {
                this.startElection();
            }
        }
    }

    startElection() {
        console.log(`Node ${this.id} starting election for term ${this.term + 1}`);
        this.state = STATES.CANDIDATE;
        this.term += 1;
        this.votedFor = this.id;
        this.votesReceived = new Set([this.id]);
        this.electionElapsed = 0;
        this.electionTimeout = this.getRandomTimeout();

        this.cluster.broadcast(this.id, RPC_TYPES.REQUEST_VOTE, {
            term: this.term,
            lastLogIndex: this.log.length - 1,
            lastLogTerm: this.log.length > 0 ? this.log[this.log.length - 1].term : 0
        });
    }

    sendHeartbeats() {
        this.cluster.broadcast(this.id, RPC_TYPES.APPEND_ENTRIES, {
            term: this.term,
            leaderId: this.id,
            prevLogIndex: this.log.length - 1,
            prevLogTerm: this.log.length > 0 ? this.log[this.log.length - 1].term : 0,
            entries: [], // Empty for heartbeats
            leaderCommit: this.commitIndex
        });
    }

    onReceiveRPC(fromId, type, data) {
        if (this.state === STATES.DEAD) return;

        // Rule: If RPC request or response contains term T > currentTerm:
        // set currentTerm = T, convert to follower
        if (data.term > this.term) {
            this.term = data.term;
            this.state = STATES.FOLLOWER;
            this.votedFor = null;
        }

        switch (type) {
            case RPC_TYPES.REQUEST_VOTE:
                this.handleRequestVote(fromId, data);
                break;
            case RPC_TYPES.VOTE_RESPONSE:
                this.handleVoteResponse(fromId, data);
                break;
            case RPC_TYPES.APPEND_ENTRIES:
                this.handleAppendEntries(fromId, data);
                break;
            case RPC_TYPES.APPEND_RESPONSE:
                // Handle replication logic if needed
                break;
        }
    }

    handleRequestVote(fromId, data) {
        let granted = false;
        if (data.term >= this.term && (this.votedFor === null || this.votedFor === fromId)) {
            // Simplified log matching for viz
            granted = true;
            this.votedFor = fromId;
            this.electionElapsed = 0; // Reset timer on voting
        }

        this.cluster.send(this.id, fromId, RPC_TYPES.VOTE_RESPONSE, {
            term: this.term,
            voteGranted: granted
        });
    }

    handleVoteResponse(fromId, data) {
        if (this.state !== STATES.CANDIDATE) return;

        if (data.voteGranted) {
            this.votesReceived.add(fromId);
            if (this.votesReceived.size > this.cluster.nodes.length / 2) {
                this.becomeLeader();
            }
        }
    }

    handleAppendEntries(fromId, data) {
        if (data.term >= this.term) {
            this.state = STATES.FOLLOWER;
            this.electionElapsed = 0; // Reset timer
            this.term = data.term;
        }

        this.cluster.send(this.id, fromId, RPC_TYPES.APPEND_RESPONSE, {
            term: this.term,
            success: true // Simplified
        });
    }

    becomeLeader() {
        console.log(`Node ${this.id} became LEADER for term ${this.term}`);
        this.state = STATES.LEADER;
        this.heartbeatElapsed = 0;
        this.sendHeartbeats();
    }

    forceTimeout() {
        this.electionElapsed = this.electionTimeout;
    }
}

class ClusterSimulation {
    constructor(nodeIds) {
        this.nodes = nodeIds.map(id => new RaftNode(id, this));
        this.messages = [];
        this.isPaused = false;
        this.speed = 1.0;
        this.elapsedTime = 0;
    }

    update(dt) {
        if (this.isPaused) return;

        const scaledDt = dt * this.speed;
        this.elapsedTime += scaledDt;

        // Update nodes
        this.nodes.forEach(node => node.update(scaledDt));

        // Update messages
        for (let i = this.messages.length - 1; i >= 0; i--) {
            const msg = this.messages[i];
            msg.remainingTime -= scaledDt;
            if (msg.remainingTime <= 0) {
                const targetNode = this.nodes.find(n => n.id === msg.to);
                if (targetNode) targetNode.onReceiveRPC(msg.from, msg.type, msg.data);
                this.messages.splice(i, 1);
            }
        }
    }

    send(from, to, type, data) {
        this.messages.push({
            from, to, type, data,
            totalTime: 500 + Math.random() * 300, // Latency
            remainingTime: 500 + Math.random() * 300
        });
    }

    broadcast(from, type, data) {
        this.nodes.forEach(node => {
            if (node.id !== from) {
                this.send(from, node.id, type, data);
            }
        });
    }

    reset() {
        const nodeIds = this.nodes.map(n => n.id);
        this.nodes = nodeIds.map(id => new RaftNode(id, this));
        this.messages = [];
        this.elapsedTime = 0;
    }
}
