var nodes;
var links;

$(document).ready(function() {
    $("#navdrawer").navdrawer({
        type: "permanent"
    });

    $.get("/web/graph?nodes=" + encodeURIComponent($("#id_nodes").val()), function(data) {
        nodes = data.nodes;
        links = data.edges;
        main();
    });
});

var COLORS = d3.schemeSet3;
var nodeRadii = {};

function main() {
    const $sidedrawerTitle = $(".navdrawer .navdrawer-header h3");
    const $sidedrawerAuthors = $(".navdrawer .navdrawer-authors");
    const $sidedrawerUrl = $(".navdrawer .navdrawer-url");
    const $sidedrawerAbstract = $(".navdrawer #collapseAbstract > .expansion-panel-body");
    const $sidedrawerInCitations = $(".navdrawer #collapseInCitations .list-group");
    const $sidedrawerOutCitations = $(".navdrawer #collapseOutCitations .list-group");

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
        .attr('fill', 'white')
        .attr('refX', 7)
        .attr('markerWidth', 8)
        .attr('markerHeight', 8)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5');

    const g = svg.append("g");

    const simulation = d3.forceSimulation()
        .force("charge", d3.forceManyBody().strength(-100))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const linkElements = g.selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke-width", 1)
        .attr("stroke", "white")
        .attr("marker-end", "url(#end-arrow)");

    const nodeElements = g.selectAll("circle")
        .data(nodes)
        .enter().append("circle")
            .attr("r", (node) => calcNodeRadius(node))
            .attr("fill", "grey")
            .attr("data-toggle", "popover")
            .attr("data-title", (node) => node.title)
            .attr("data-content", (node) => node.authors);

    const textElements = g.selectAll("text")
        .data(nodes)
        .enter().append("text")
            .text(node => node.label)
            .attr("font-size", 14)
            .attr("dx", (node) => getLabelOffset(node))
            .attr("dy", 5);

    function isNeighborLink(node, link) {
        return link.target.id === node.id || link.source.id === node.id;
    }

    function getNodeColor(node, neighbors) {
        return COLORS[node.group % COLORS.length];
    }

    function getTextColor(node, neighbors) {
        return neighbors.includes(node.id) ? "white" : "#ddd";
    }

    function calcNodeRadius(node) {
        nodeRadii[node.id] = 5 + Math.log(node.indegree + Math.E) * 8;
        return nodeRadii[node.id];
    }

    function getLabelOffset(node) {
        return 5 + nodeRadii[node.id];
    }

    function getLinkColor(node, link) {
        return isNeighborLink(node, link) ? "#bbb" : "#888";
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
            $sidedrawerInCitations.empty();
            for (var i = 0; i < data.inward.length; i++) {
                const $citation = $(document.createElement("li"));
                $citation.addClass("list-group-item");
                $citation.text(data.inward[i].title);
                $sidedrawerInCitations.append($citation);
            }
            $sidedrawerOutCitations.empty();
            for (var i = 0; i < data.outward.length; i++) {
                const $citation = $(document.createElement("li"));
                $citation.addClass("list-group-item");
                $citation.text(data.outward[i].title);
                $sidedrawerOutCitations.append($citation);
            }
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
            .attr("x2", link => {
                const targetPadding = 2 + nodeRadii[link.target.id];
                const deltaX = link.target.x - link.source.x;
                const deltaY = link.target.y - link.source.y;
                const dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
                const normX = deltaX / dist;
                return link.target.x - (targetPadding * normX);
            })
            .attr("y2", link => {
                const targetPadding = 2 + nodeRadii[link.target.id];
                const deltaX = link.target.x - link.source.x;
                const deltaY = link.target.y - link.source.y;
                const dist = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
                const normY = deltaY / dist;
                return link.target.y - (targetPadding * normY);
            });
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
