const svg = document.getElementById('networkSvg');
const logGrid = document.getElementById('logGrid');
const nodeDetail = document.getElementById('nodeDetail');
const detailNodeId = document.getElementById('detailNodeId');
const detailState = document.getElementById('detailState');
const detailTerm = document.getElementById('detailTerm');
const detailVotedFor = document.getElementById('detailVotedFor');
const playPauseBtn = document.getElementById('playPauseBtn');
const speedSlider = document.getElementById('speedSlider');
const resetBtn = document.getElementById('resetBtn');
const elapsedTimeDisplay = document.getElementById('elapsedTime');

const nodeIds = ['S1', 'S2', 'S3', 'S4', 'S5'];
const sim = new ClusterSimulation(nodeIds);
let selectedNodeId = null;

// Layout Constants
const WIDTH = 800;
const HEIGHT = 600;
const CENTER_X = WIDTH / 2;
const CENTER_Y = HEIGHT / 2;
const RADIUS = 200;
const NODE_RADIUS = 40;

function initViz() {
    nodeIds.forEach((id, index) => {
        const angle = (index / nodeIds.length) * Math.PI * 2 - Math.PI / 2;
        const x = CENTER_X + Math.cos(angle) * RADIUS;
        const y = CENTER_Y + Math.sin(angle) * RADIUS;

        // Group for node
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('id', `node-group-${id}`);
        g.setAttribute('transform', `translate(${x}, ${y})`);
        g.classList.add('node-group');
        g.addEventListener('click', () => selectNode(id));

        // Timeout Ring Background
        const ringBg = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        ringBg.setAttribute('r', NODE_RADIUS + 8);
        ringBg.classList.add('timeout-ring');
        g.appendChild(ringBg);

        // Timeout Progress
        const ringProgress = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        ringProgress.setAttribute('r', NODE_RADIUS + 8);
        ringProgress.classList.add('timeout-progress');
        const circumference = 2 * Math.PI * (NODE_RADIUS + 8);
        ringProgress.style.strokeDasharray = circumference;
        ringProgress.style.strokeDashoffset = circumference;
        ringProgress.setAttribute('id', `timeout-progress-${id}`);
        g.appendChild(ringProgress);

        // Main Node Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('r', NODE_RADIUS);
        circle.setAttribute('id', `node-circle-${id}`);
        circle.classList.add('node-circle');
        g.appendChild(circle);

        // Label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('dy', '5');
        text.setAttribute('text-anchor', 'middle');
        text.classList.add('node-label');
        text.textContent = id;
        g.appendChild(text);

        svg.appendChild(g);
    });

    // Start Animation Loop
    requestAnimationFrame(update);
}

function selectNode(id) {
    selectedNodeId = id;
    nodeDetail.classList.remove('hidden');
    updateNodeDetail();
    
    // Highlight selected node
    document.querySelectorAll('.node-circle').forEach(c => c.style.stroke = 'none');
    document.getElementById(`node-circle-${id}`).style.stroke = 'var(--accent-blue)';
    document.getElementById(`node-circle-${id}`).style.strokeWidth = '3px';
}

function updateNodeDetail() {
    if (!selectedNodeId) return;
    const node = sim.nodes.find(n => n.id === selectedNodeId);
    detailNodeId.textContent = node.id;
    detailState.textContent = node.state.charAt(0).toUpperCase() + node.state.slice(1);
    detailTerm.textContent = node.term;
    detailVotedFor.textContent = node.votedFor || 'None';
    
    // Update colors based on state
    detailState.style.color = `var(--${node.state}-color)`;
}

let lastTime = 0;
function update(time) {
    const dt = time - lastTime;
    lastTime = time;

    if (dt > 0) {
        sim.update(dt);
        render();
    }
    requestAnimationFrame(update);
}

function render() {
    // Update Nodes
    sim.nodes.forEach(node => {
        const circle = document.getElementById(`node-circle-${node.id}`);
        const progress = document.getElementById(`timeout-progress-${node.id}`);
        
        // Update Colors
        circle.style.fill = `var(--${node.state}-color)`;
        
        // Update Progress Ring
        if (node.state === STATES.LEADER) {
            progress.style.strokeDashoffset = 0;
            progress.style.stroke = 'var(--leader-color)';
        } else {
            const ratio = node.electionElapsed / node.electionTimeout;
            const circumference = 2 * Math.PI * (NODE_RADIUS + 8);
            progress.style.strokeDashoffset = circumference * (1 - ratio);
            progress.style.stroke = `var(--${node.state}-color)`;
        }
    });

    // Update Messages (Pulses)
    // Clear old message elements
    const oldMessages = document.querySelectorAll('.rpc-pulse');
    oldMessages.forEach(m => m.remove());

    sim.messages.forEach(msg => {
        const fromNode = sim.nodes.find(n => n.id === msg.from);
        const toNode = sim.nodes.find(n => n.id === msg.to);
        
        const indexFrom = nodeIds.indexOf(msg.from);
        const indexTo = nodeIds.indexOf(msg.to);
        
        const angleFrom = (indexFrom / nodeIds.length) * Math.PI * 2 - Math.PI / 2;
        const xFrom = CENTER_X + Math.cos(angleFrom) * RADIUS;
        const yFrom = CENTER_Y + Math.sin(angleFrom) * RADIUS;
        
        const angleTo = (indexTo / nodeIds.length) * Math.PI * 2 - Math.PI / 2;
        const xTo = CENTER_X + Math.cos(angleTo) * RADIUS;
        const yTo = CENTER_Y + Math.sin(angleTo) * RADIUS;
        
        const ratio = 1 - (msg.remainingTime / msg.totalTime);
        const curX = xFrom + (xTo - xFrom) * ratio;
        const curY = yFrom + (yTo - yFrom) * ratio;
        
        const pulse = document.createElement('div');
        pulse.classList.add('rpc-pulse');
        pulse.classList.add(msg.type.includes('append') ? 'heartbeat' : 'vote');
        pulse.style.left = `${curX}px`;
        pulse.style.top = `${curY}px`;
        pulse.style.transform = 'translate(-50%, -50%)';
        
        document.getElementById('simulationCanvas').appendChild(pulse);
    });

    elapsedTimeDisplay.textContent = `${(sim.elapsedTime / 1000).toFixed(1)}s`;
    updateNodeDetail();
}

// UI Listeners
playPauseBtn.addEventListener('click', () => {
    sim.isPaused = !sim.isPaused;
    document.querySelector('.icon-pause').classList.toggle('hidden', sim.isPaused);
    document.querySelector('.icon-play').classList.toggle('hidden', !sim.isPaused);
});

speedSlider.addEventListener('input', (e) => {
    sim.speed = parseFloat(e.target.value);
});

resetBtn.addEventListener('click', () => {
    sim.reset();
});

document.getElementById('btnTimeout').addEventListener('click', () => {
    if (selectedNodeId) {
        const node = sim.nodes.find(n => n.id === selectedNodeId);
        node.forceTimeout();
    }
});

initViz();
