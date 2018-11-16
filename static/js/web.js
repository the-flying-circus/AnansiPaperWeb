nodes = [
    {id: "node1", group: 0, label: "Node 1"},
    {id: "node2", group: 1, label: "Node 2"},
    {id: "node3", group: 1, label: "Node 3"},
    {id: "node4", group: 1, label: "Node 4"},
    {id: "node5", group: 1, label: "Node 5"},
    {id: "node6", group: 0, label: "Node 6"},
]

groups = {
    0: "this",
    1: "that",
}

links = [
    {target: "node1", source: "node2", strength: 0.1},
    {target: "node5", source: "node4", strength: 0.1},
    {target: "node5", source: "node6", strength: 0.1},
]

$(document).ready(function() {
    const $container = $("#web-container");
    const width = $container.width();
    const height = $container.height();

    const svg = d3.select("#web-container")
        .attr("width", width)
        .attr("height", height);

    const simulation = d3.forceSimulation()
        .force("charge", d3.forceManyBody().strength(-100))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const linkElements = svg.append("g")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke-width", 1)
        .attr("stroke", "black");

    const nodeElements = svg.append("g")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
            .attr("r", 10)
            .attr("fill", "grey");

    const textElements = svg.append("g")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
            .text(node => node.label)
            .attr("font-size", 14)
            .attr("dx", 15)
            .attr("dy", 4);

    function isNeighborLink(node, link) {
        return link.target.id === node.id || link.source.id === node.id;
    }

    function getNodeColor(node, neighbors) {
        if (node.group === 0)
            return neighbors.includes(node.id) ? "black" : "grey";
        if (node.group === 1)
            return neighbors.includes(node.id) ? "red" : "pink";
    }

    function getTextColor(node, neighbors) {
        return neighbors.includes(node.id) ? "black" : "grey";
    }

    function getLinkColor(node, link) {
        return isNeighborLink(node, link) ? "black" : "grey";
    }

    function getNeighbors(node) {
        return links.reduce((neighbors, link) => {
            if (link.target.id === node.id)
                neighbors.push(link.source.id);
            else if (link.source.id === node.id)
                neighbors.push(link.target.id);
            return neighbors;
        }, [node.id]);
    }

    function selectNode(selectedNode) {
        const neighbors = getNeighbors(selectedNode);
        nodeElements.attr("fill", node => getNodeColor(node, neighbors));
        textElements.attr("fill", node => getTextColor(node, neighbors));
        linkElements.attr("stroke", link => getLinkColor(selectedNode, link));
    }

    simulation.nodes(nodes).on("tick", () => {
        linkElements
            .attr("x1", link => link.source.x)
            .attr("y1", link => link.source.y)
            .attr("x2", link => link.target.x)
            .attr("y2", link => link.target.y);
        nodeElements
            .attr("cx", node => node.x)
            .attr("cy", node => node.y);
        textElements
            .attr("x", node => node.x)
            .attr("y", node => node.y);
    });

    simulation.force("link", d3.forceLink()
        .id(link => link.id)
        .strength(link => link.strength));
    simulation.force("link").links(links);

    selectNode(nodes[0]);
    nodeElements.on("click", selectNode);
    $(window).resize(function() {
        const width = $container.width();
        const height = $container.height();
        svg.attr("width", width).attr("height", height);
        simulation.force("center", d3.forceCenter(width / 2, height / 2));
    });

    function zoomed() {
        svg.attr("transform", "translate(" + d3.event.transform.x + "," + d3.event.transform.y + ")scale(" + d3.event.transform.k + ")");
    }

    svg.call(d3.zoom().on("zoom", zoomed));
});
