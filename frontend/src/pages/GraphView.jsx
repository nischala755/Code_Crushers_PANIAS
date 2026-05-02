import { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import API from '../api/client';

const DEPT_COLORS = {
  SHOPS_ESTABLISHMENT: '#3498db',
  FACTORIES: '#e67e22',
  LABOUR: '#2ecc71',
  POLLUTION_BOARD: '#9b59b6',
};

export default function GraphView() {
  const svgRef = useRef(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    setLoading(true);
    API.get('/graph/', { params: { limit, min_score: 0.4 } })
      .then(r => { setGraphData(r.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [limit]);

  useEffect(() => {
    if (!graphData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth || 900;
    const height = 500;

    // Defs for arrow markers and gradients
    const defs = svg.append('defs');

    // Arrow marker
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#cbd5e1');

    const nodes = graphData.nodes.map(n => ({ ...n }));
    const nodeIds = new Set(nodes.map(n => n.id));
    const edges = graphData.edges
      .filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
      .map(e => ({ ...e }));

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id(d => d.id).distance(80).strength(0.4))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(25));

    // Container group for zoom
    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.3, 4])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Links
    const link = g.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', d => Math.max(1, d.weight * 3))
      .attr('stroke-opacity', 0.6);

    // Nodes
    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(d3.drag()
        .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    // Node circles
    node.append('circle')
      .attr('r', d => d.type === 'ubid' ? 12 : 7)
      .attr('fill', d => {
        if (d.type === 'ubid') return '#1b2a4a';
        return DEPT_COLORS[d.department] || '#6b7280';
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', d => d.type === 'ubid' ? 2 : 1);

    // Node labels
    node.append('text')
      .text(d => d.type === 'ubid' ? d.id : d.label.substring(0, 15))
      .attr('font-size', d => d.type === 'ubid' ? '8px' : '7px')
      .attr('font-weight', d => d.type === 'ubid' ? 700 : 400)
      .attr('fill', '#334155')
      .attr('text-anchor', 'middle')
      .attr('dy', d => d.type === 'ubid' ? -16 : -10);

    // Tooltip
    node.append('title')
      .text(d => `${d.id}\n${d.label}\n${d.type === 'record' ? d.department : 'UBID Cluster'}`);

    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [graphData]);

  return (
    <div>
      <div className="flex-between mb-3">
        <h2 className="page-title" style={{ marginBottom: 0 }}>Entity Graph View</h2>
        <div className="flex gap-2">
          <select className="form-select" value={limit} onChange={e => setLimit(Number(e.target.value))}>
            <option value={10}>10 clusters</option>
            <option value={20}>20 clusters</option>
            <option value={30}>30 clusters</option>
            <option value={50}>50 clusters</option>
          </select>
        </div>
      </div>

      <div className="flex gap-3 mb-3">
        {Object.entries(DEPT_COLORS).map(([dept, color]) => (
          <span key={dept} className="text-xs flex gap-2" style={{ alignItems: 'center' }}>
            <span style={{ width: 10, height: 10, background: color, display: 'inline-block' }} />
            {dept.split('_')[0]}
          </span>
        ))}
        <span className="text-xs flex gap-2" style={{ alignItems: 'center' }}>
          <span style={{ width: 12, height: 12, background: '#1b2a4a', display: 'inline-block', borderRadius: '50%' }} />
          UBID Node
        </span>
      </div>

      <div className="graph-container">
        {loading ? (
          <div className="loading-spinner">Loading graph data...</div>
        ) : (
          <svg ref={svgRef} />
        )}
      </div>
    </div>
  );
}
