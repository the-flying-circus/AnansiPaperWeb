var nodes;
var links;

$.get("/web/graph", function(data) {
    nodes = data.nodes;
    links = data.edges;
    main();
});

$(document).ready(function() {
    $("#navdrawer").navdrawer({
        type: "permanent"
    });
});

COLORS = d3.schemeCategory10;

function main() {
    var $sidedrawerTitle = $(".navdrawer .navdrawer-header h3");
    var $sidedrawerAuthors = $(".navdrawer .navdrawer-authors");
    var $sidedrawerUrl = $(".navdrawer .navdrawer-url");
    var $sidedrawerAbstract = $(".navdrawer #collapseAbstract > .expansion-panel-body");

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
        .call(zoom.scaleExtent([0.5, 8]).on("zoom", zoomed));
    svg.append('svg:defs').append('svg:marker')
        .attr('id', 'end-arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 22)
        .attr('markerWidth', 8)
        .attr('markerHeight', 8)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5');

    const g = svg.append("g");

    const simulation = d3.forceSimulation()
        .force("charge", d3.forceManyBody().strength(-70))
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
            .text(node => node.label)
            .attr("font-size", 14)
            .attr("dx", 14)
            .attr("dy", 5);

    function isNeighborLink(node, link) {
        return link.target.id === node.id || link.source.id === node.id;
    }

    function getNodeColor(node, neighbors) {
        return COLORS[node.group % COLORS.length];
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
            .scale(3)
            .translate(-selectedNode.x, -selectedNode.y);
    }

    function selectNode(node) {
        selectedNode = node;
        const neighbors = getNeighbors(selectedNode);
        textElements.attr("fill", node => getTextColor(node, neighbors));
        linkElements.attr("stroke", link => getLinkColor(selectedNode, link));
        svg.transition().duration(500).call(zoom.transform, transitionFocus);

        $.get("/web/node?id=" + selectedNode.id, function(data) {
            $sidedrawerTitle.text(data.title);
            var authors = "";
            for (var i = 0; i < data.authors.length; i++) {
                authors += data.authors[i].name + ", ";
            }
            authors = authors.substring(0, authors.length - 2);
            $sidedrawerAuthors.text(authors);
            $sidedrawerUrl.text(data.url);
            $sidedrawerUrl.attr("href", data.url);
            $sidedrawerAbstract.text(data.abstract);
        });
    }

    selectedNode = nodes[0];
    const neighbors = getNeighbors(selectedNode);
    nodeElements.attr("fill", node => getNodeColor(node, neighbors));
    textElements.attr("fill", node => getTextColor(node, neighbors));
    linkElements.attr("stroke", link => getLinkColor(selectedNode, link));

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
        .strength(link => 0.05));
    simulation.force("link").links(links);

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
}
