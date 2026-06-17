/* ============================================
   CONCEPT GRAPH - Interactive Mind Map
   Force-Directed Graph using Canvas
   ============================================ */

const ConceptGraph = {
  // Données du graphe
  data: {
    nodes: [
      // Centre
      { id: 'protein', label: 'تركيب البروتين', tag: 'محور', type: 'center', desc: 'العملية الأساسية لإنتاج البروتينات من المعلومة الوراثية في الـADN.' },
      
      // Niveau 1 - Concepts principaux
      { id: 'adn', label: 'ADN', tag: 'جزيء', type: 'main', desc: 'الحمض النووي الريبوزي منقوص الأكسجين، يحمل المعلومة الوراثية.' },
      { id: 'arnm', label: 'ARNm', tag: 'جزيء', type: 'main', desc: 'الحمض النووي الريبوزي الرسول، ينقل المعلومة من النواة إلى الهيولى.' },
      { id: 'ribosome', label: 'الريبوزوم', tag: 'عضية', type: 'main', desc: 'مقر تركيب البروتين، يتكون من وحدتين تحت ريبوزوميتين.' },
      { id: 'protein-final', label: 'البروتين', tag: 'منتج', type: 'main', desc: 'الناتج النهائي، سلسلة من الأحماض الأمينية ذات بنية فراغية وظيفية.' },
      
      // Niveau 2 - Processus
      { id: 'transcription', label: 'الاستنساخ', tag: 'عملية', type: 'process', desc: 'نسخ المعلومة من ADN إلى ARNm داخل النواة.' },
      { id: 'translation', label: 'الترجمة', tag: 'عملية', type: 'process', desc: 'تحويل المعلومة من ARNm إلى بروتين على الريبوزومات.' },
      
      // Niveau 3 - Détails
      { id: 'arn-poly', label: 'ARN polymérase', tag: 'إنزيم', type: 'detail', desc: 'الإنزيم المسؤول عن عملية الاستنساخ.' },
      { id: 'code', label: 'الشفرة الوراثية', tag: 'مفهوم', type: 'detail', desc: '64 رامزة تربط بين النيوكليوتيدات والأحماض الأمينية.' },
      { id: 'arnt', label: 'ARNt', tag: 'جزيء', type: 'detail', desc: 'ARN الناقل، يجلب الأحماض الأمينية إلى الريبوزوم.' },
      { id: 'aa', label: 'الأحماض الأمينية', tag: 'وحدة بناء', type: 'detail', desc: '20 نوعاً، تشكل الوحدات البنائية للبروتينات.' },
      { id: 'codon', label: 'الرامزة (Codon)', tag: 'مفهوم', type: 'detail', desc: 'تتابع 3 نيوكليوتيدات يشفر لحمض أميني واحد.' },
      { id: 'start', label: 'رامزة الانطلاق', tag: 'إشارة', type: 'detail', desc: 'AUG - تبدأ عملية الترجمة وتشفر للميثيونين.' },
      { id: 'stop', label: 'رامزات التوقف', tag: 'إشارة', type: 'detail', desc: 'UAA, UAG, UGA - توقف عملية الترجمة.' }
    ],
    
    edges: [
      // Centre vers niveau 1
      { from: 'protein', to: 'adn' },
      { from: 'protein', to: 'arnm' },
      { from: 'protein', to: 'ribosome' },
      { from: 'protein', to: 'protein-final' },
      
      // Processus
      { from: 'adn', to: 'transcription' },
      { from: 'transcription', to: 'arnm' },
      { from: 'arnm', to: 'translation' },
      { from: 'translation', to: 'protein-final' },
      { from: 'ribosome', to: 'translation' },
      
      // Détails
      { from: 'transcription', to: 'arn-poly' },
      { from: 'translation', to: 'arnt' },
      { from: 'translation', to: 'code' },
      { from: 'arnt', to: 'aa' },
      { from: 'aa', to: 'protein-final' },
      { from: 'code', to: 'codon' },
      { from: 'codon', to: 'start' },
      { from: 'codon', to: 'stop' }
    ]
  },
  
  // Couleurs par type
  colors: {
    center: { bg: '#C9A961', border: '#A68845', text: '#1a1a2e' },
    main: { bg: '#A78BFA', border: '#7C5FCD', text: '#fff' },
    process: { bg: '#FB7185', border: '#E11D48', text: '#fff' },
    detail: { bg: '#60A5FA', border: '#2563EB', text: '#fff' }
  },
  
  // État
  state: {
    canvas: null,
    ctx: null,
    nodes: [],
    edges: [],
    selectedNode: null,
    hoveredNode: null,
    isDragging: false,
    draggedNode: null,
    offsetX: 0,
    offsetY: 0,
    scale: 1,
    panX: 0,
    panY: 0,
    isPanning: false,
    lastMouseX: 0,
    lastMouseY: 0,
    animationFrame: null
  },
  
  init() {
    const container = document.getElementById('graphContainer');
    if (!container) return;
    
    this.setupCanvas(container);
    this.initializeNodes();
    this.attachEventListeners();
    this.startAnimation();
  },
  
  setupCanvas(container) {
    this.state.canvas = document.getElementById('graphCanvas');
    this.state.ctx = this.state.canvas.getContext('2d');
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  },
  
  resizeCanvas() {
    const canvas = this.state.canvas;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    this.state.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  },
  
  initializeNodes() {
    const canvas = this.state.canvas;
    const w = canvas.width / window.devicePixelRatio;
    const h = canvas.height / window.devicePixelRatio;
    const centerX = w / 2;
    const centerY = h / 2;
    
    this.state.nodes = this.data.nodes.map((node, i) => {
      let x, y, radius;
      
      if (node.type === 'center') {
        x = centerX; y = centerY; radius = 50;
      } else if (node.type === 'main') {
        const angle = (i - 1) * (Math.PI * 2 / 4);
        x = centerX + Math.cos(angle) * 180;
        y = centerY + Math.sin(angle) * 180;
        radius = 40;
      } else if (node.type === 'process') {
        const angle = Math.random() * Math.PI * 2;
        x = centerX + Math.cos(angle) * 280;
        y = centerY + Math.sin(angle) * 280;
        radius = 38;
      } else {
        const angle = Math.random() * Math.PI * 2;
        x = centerX + Math.cos(angle) * 350;
        y = centerY + Math.sin(angle) * 350;
        radius = 32;
      }
      
      return {
        ...node,
        x, y, vx: 0, vy: 0, radius
      };
    });
    
    this.state.edges = this.data.edges.map(edge => ({
      from: this.state.nodes.find(n => n.id === edge.from),
      to: this.state.nodes.find(n => n.id === edge.to)
    }));
  },
  
  applyForces() {
    const nodes = this.state.nodes;
    const edges = this.state.edges;
    
    // Repulsion entre tous les nœuds
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1;
        const force = 3000 / (dist * dist);
        
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        
        if (nodes[i].type !== 'center' && !nodes[i].isDragging) {
          nodes[i].vx -= fx;
          nodes[i].vy -= fy;
        }
        if (nodes[j].type !== 'center' && !nodes[j].isDragging) {
          nodes[j].vx += fx;
          nodes[j].vy += fy;
        }
      }
    }
    
    // Attraction sur les arêtes
    edges.forEach(edge => {
      const dx = edge.to.x - edge.from.x;
      const dy = edge.to.y - edge.from.y;
      const dist = Math.sqrt(dx*dx + dy*dy) || 1;
      const targetDist = 150;
      const force = (dist - targetDist) * 0.03;
      
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      
      if (edge.from.type !== 'center' && !edge.from.isDragging) {
        edge.from.vx += fx;
        edge.from.vy += fy;
      }
      if (edge.to.type !== 'center' && !edge.to.isDragging) {
        edge.to.vx -= fx;
        edge.to.vy -= fy;
      }
    });
    
    // Appliquer vitesse et damping
    nodes.forEach(node => {
      if (node.type === 'center' || node.isDragging) return;
      node.vx *= 0.85;
      node.vy *= 0.85;
      node.x += node.vx;
      node.y += node.vy;
    });
  },
  
  draw() {
    const ctx = this.state.ctx;
    const canvas = this.state.canvas;
    const w = canvas.width / window.devicePixelRatio;
    const h = canvas.height / window.devicePixelRatio;
    
    ctx.clearRect(0, 0, w, h);
    
    // Transformation pan & zoom
    ctx.save();
    ctx.translate(this.state.panX, this.state.panY);
    ctx.scale(this.state.scale, this.state.scale);
    
    // Dessiner les arêtes
    this.state.edges.forEach(edge => {
      const isHighlighted = this.state.selectedNode && 
        (edge.from.id === this.state.selectedNode.id || edge.to.id === this.state.selectedNode.id);
      
      ctx.beginPath();
      ctx.moveTo(edge.from.x, edge.from.y);
      ctx.lineTo(edge.to.x, edge.to.y);
      ctx.strokeStyle = isHighlighted ? 'rgba(201, 169, 97, 0.8)' : 'rgba(255, 255, 255, 0.15)';
      ctx.lineWidth = isHighlighted ? 2.5 : 1;
      ctx.stroke();
    });
    
    // Dessiner les nœuds
    this.state.nodes.forEach(node => {
      const color = this.colors[node.type];
      const isHovered = this.state.hoveredNode && this.state.hoveredNode.id === node.id;
      const isSelected = this.state.selectedNode && this.state.selectedNode.id === node.id;
      const isConnected = this.state.selectedNode && this.state.edges.some(e =>
        (e.from.id === this.state.selectedNode.id && e.to.id === node.id) ||
        (e.to.id === this.state.selectedNode.id && e.from.id === node.id)
      );
      
      // Halo si sélectionné ou survolé
      if (isSelected || isHovered || isConnected) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 8, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? 'rgba(201, 169, 97, 0.35)' : 'rgba(201, 169, 97, 0.2)';
        ctx.fill();
      }
      
      // Cercle principal
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = color.bg;
      ctx.fill();
      ctx.strokeStyle = color.border;
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Texte
      ctx.fillStyle = color.text;
      ctx.font = `bold ${node.type === 'center' ? 14 : 11}px Cairo, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Wrap text si trop long
      const maxWidth = node.radius * 1.6;
      const words = node.label.split(' ');
      let line = '';
      const lines = [];
      
      words.forEach(word => {
        const testLine = line + word + ' ';
        const metrics = ctx.measureText(testLine);
        if (metrics.width > maxWidth && line !== '') {
          lines.push(line.trim());
          line = word + ' ';
        } else {
          line = testLine;
        }
      });
      lines.push(line.trim());
      
      const lineHeight = node.type === 'center' ? 16 : 13;
      const startY = node.y - ((lines.length - 1) * lineHeight) / 2;
      lines.forEach((l, i) => {
        ctx.fillText(l, node.x, startY + i * lineHeight);
      });
    });
    
    ctx.restore();
  },
  
  startAnimation() {
    const animate = () => {
      this.applyForces();
      this.draw();
      this.state.animationFrame = requestAnimationFrame(animate);
    };
    animate();
  },
  
  getMousePos(e) {
    const rect = this.state.canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - this.state.panX) / this.state.scale;
    const y = (e.clientY - rect.top - this.state.panY) / this.state.scale;
    return { x, y };
  },
  
  getNodeAtPos(x, y) {
    for (let i = this.state.nodes.length - 1; i >= 0; i--) {
      const node = this.state.nodes[i];
      const dx = x - node.x;
      const dy = y - node.y;
      if (Math.sqrt(dx*dx + dy*dy) < node.radius) {
        return node;
      }
    }
    return null;
  },
  
  attachEventListeners() {
    const canvas = this.state.canvas;
    
    canvas.addEventListener('mousedown', (e) => {
      const pos = this.getMousePos(e);
      const node = this.getNodeAtPos(pos.x, pos.y);
      
      if (node) {
        this.state.draggedNode = node;
        node.isDragging = true;
        this.state.offsetX = pos.x - node.x;
        this.state.offsetY = pos.y - node.y;
      } else {
        this.state.isPanning = true;
        this.state.lastMouseX = e.clientX;
        this.state.lastMouseY = e.clientY;
      }
    });
    
    canvas.addEventListener('mousemove', (e) => {
      const pos = this.getMousePos(e);
      
      if (this.state.draggedNode) {
        this.state.draggedNode.x = pos.x - this.state.offsetX;
        this.state.draggedNode.y = pos.y - this.state.offsetY;
      } else if (this.state.isPanning) {
        this.state.panX += e.clientX - this.state.lastMouseX;
        this.state.panY += e.clientY - this.state.lastMouseY;
        this.state.lastMouseX = e.clientX;
        this.state.lastMouseY = e.clientY;
      } else {
        const hovered = this.getNodeAtPos(pos.x, pos.y);
        this.state.hoveredNode = hovered;
        canvas.style.cursor = hovered ? 'pointer' : 'grab';
      }
    });
    
    canvas.addEventListener('mouseup', (e) => {
      if (this.state.draggedNode && !this.state.draggedNode._moved) {
        // Clic sur un nœud (sans déplacement)
        this.selectNode(this.state.draggedNode);
      }
      if (this.state.draggedNode) {
        this.state.draggedNode.isDragging = false;
        this.state.draggedNode = null;
      }
      this.state.isPanning = false;
    });
    
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      this.state.scale = Math.max(0.3, Math.min(2.5, this.state.scale * delta));
    });
    
    // Touch support
    canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        const pos = this.getMousePos(touch);
        const node = this.getNodeAtPos(pos.x, pos.y);
        if (node) {
          this.state.draggedNode = node;
          node.isDragging = true;
          this.state.offsetX = pos.x - node.x;
          this.state.offsetY = pos.y - node.y;
        } else {
          this.state.isPanning = true;
          this.state.lastMouseX = touch.clientX;
          this.state.lastMouseY = touch.clientY;
        }
      }
    }, { passive: false });
    
    canvas.addEventListener('touchmove', (e) => {
      e.preventDefault();
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        if (this.state.draggedNode) {
          const pos = this.getMousePos(touch);
          this.state.draggedNode.x = pos.x - this.state.offsetX;
          this.state.draggedNode.y = pos.y - this.state.offsetY;
        } else if (this.state.isPanning) {
          this.state.panX += touch.clientX - this.state.lastMouseX;
          this.state.panY += touch.clientY - this.state.lastMouseY;
          this.state.lastMouseX = touch.clientX;
          this.state.lastMouseY = touch.clientY;
        }
      }
    }, { passive: false });
    
    canvas.addEventListener('touchend', (e) => {
      if (this.state.draggedNode) {
        this.selectNode(this.state.draggedNode);
        this.state.draggedNode.isDragging = false;
        this.state.draggedNode = null;
      }
      this.state.isPanning = false;
    });
    
    // Controls
    document.getElementById('graphZoomIn')?.addEventListener('click', () => {
      this.state.scale = Math.min(2.5, this.state.scale * 1.2);
    });
    document.getElementById('graphZoomOut')?.addEventListener('click', () => {
      this.state.scale = Math.max(0.3, this.state.scale * 0.8);
    });
    document.getElementById('graphReset')?.addEventListener('click', () => {
      this.state.scale = 1;
      this.state.panX = 0;
      this.state.panY = 0;
      this.initializeNodes();
    });
    
    // Search
    const searchInput = document.getElementById('graphSearch');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (query) {
          const found = this.state.nodes.find(n => n.label.toLowerCase().includes(query));
          if (found) {
            this.selectNode(found);
            // Centrer sur le nœud
            const canvas = this.state.canvas;
            const w = canvas.width / window.devicePixelRatio;
            const h = canvas.height / window.devicePixelRatio;
            this.state.panX = w/2 - found.x * this.state.scale;
            this.state.panY = h/2 - found.y * this.state.scale;
          }
        }
      });
    }
    
    // Close info panel
    document.getElementById('infoPanelClose')?.addEventListener('click', () => {
      this.state.selectedNode = null;
      document.getElementById('graphInfoPanel').classList.remove('active');
    });
  },
  
  selectNode(node) {
    this.state.selectedNode = node;
    const panel = document.getElementById('graphInfoPanel');
    if (!panel) return;
    
    const connectedCount = this.state.edges.filter(e => 
      e.from.id === node.id || e.to.id === node.id
    ).length;
    
    panel.innerHTML = `
      <button class="info-panel-close" id="infoPanelClose">✕</button>
      <span class="info-panel-tag">${node.tag}</span>
      <div class="info-panel-title">${node.label}</div>
      <div class="info-panel-desc">${node.desc}</div>
      <div class="info-panel-links">
        🔗 ${connectedCount} اتصال مع مفاهيم أخرى
      </div>
      <div class="info-panel-actions">
        <button class="info-action-btn" onclick="Chatbot.toggleChat(); setTimeout(() => { document.getElementById('chatbotInput').value = 'اشرح لي ${node.label}'; }, 400);">
          🤖 اسأل خوارزمي
        </button>
        <button class="info-action-btn secondary" onclick="ConceptGraph.deselect();">
          إغلاق
        </button>
      </div>
    `;
    panel.classList.add('active');
    
    // Re-attach close
    document.getElementById('infoPanelClose')?.addEventListener('click', () => this.deselect());
  },
  
  deselect() {
    this.state.selectedNode = null;
    document.getElementById('graphInfoPanel')?.classList.remove('active');
  }
};

// Auto-init
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('graphContainer')) {
    ConceptGraph.init();
  }
});
