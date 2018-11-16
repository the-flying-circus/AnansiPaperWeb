//$.get("/web/search?q=Neurobiology", function(data) {
//    nodes = data.nodes;
//    links = data.links;
//});

nodes = [
    {id: "node1", authors: "Bill Lee, Bob Ert", title: "How Things Stuff", isCool: true},
    {id: "node2", authors: "Sal Lee, Frank Yi", title: "How Stuff Things", isCool: false},
    {id: "node3", authors: "Grey Son", title: "How Things Stuff", isCool: false},
    {id: "node4", authors: "Sue San, Char Lee", title: "How Things Stuff", isCool: true},
]

links = [
    {target: "node1", source: "node2", strength: 0.1},
    {target: "node2", source: "node3", strength: 0.1},
]

$(document).ready(function() {
    $("#navdrawer").navdrawer({
        type: "permanent"
    });

    function zoomed() {
        g.attr("transform", d3.event.transform);
    }
    const zoom = d3.zoom();

    const $container = $("#web-container");
    var width = $container.width();
    var height = $container.height();
    var selectedNode;

    const svg = d3.select("#web-container")
        .attr("width", width)
        .attr("height", height)
        .call(zoom.scaleExtent([1, 8]).on("zoom", zoomed));
    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'end-arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 34)
        .attr('markerWidth', 4)
        .attr('markerHeight', 4)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#000');

    const g = svg.append("g");

    const simulation = d3.forceSimulation()
        .force("charge", d3.forceManyBody().strength(-100))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const linkElements = g.selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke-width", 1)
        .attr("stroke", "black")
        .attr("marker-end", "url(#end-arrow)");

    const nodeElements = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
            .attr("r", 10)
            .attr("fill", "grey")
            .attr("data-toggle", "popover")
            .attr("data-title", (node) => node.title)
            .attr("data-content", (node) => node.authors);

    const textElements = g.selectAll("text")
        .data(nodes)
        .enter().append("text")
            .text(node => node.authors)
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

    function transitionFocus() {
        return d3.zoomIdentity
            .translate(width / 2, height / 2)
            .scale(4)
            .translate(-selectedNode.x, -selectedNode.y);
    }

    function selectNode(node) {
        selectedNode = node;
        const neighbors = getNeighbors(selectedNode);
        nodeElements.attr("fill", node => getNodeColor(node, neighbors));
        textElements.attr("fill", node => getTextColor(node, neighbors));
        linkElements.attr("stroke", link => getLinkColor(selectedNode, link));

        svg.transition().duration(500).call(zoom.transform, transitionFocus);
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
    nodeElements.on("mouseover", function() {
        $(this).popover("show");
    });
    nodeElements.on("mouseout", function() {
        $(this).popover("hide");
    });
    $(window).resize(function() {
        width = $container.width();
        height = $container.height();
        svg.attr("width", width).attr("height", height);
        //simulation.force("center", d3.forceCenter(width / 2, height / 2));
    });
});
