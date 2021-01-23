
var simple_chart_config = {
	chart: {
		container: "#OrganiseChart-simple",
		animateOnInit: true
	},
	
	nodeStructure: {
		text: { name: "Parent node" },
		children: [
			{
				text: { name: "First child" }
			},
			{
				text: { name: "Second child" }
			}
		]
	}
};

// // // // // // // // // // // // // // // // // // // // // // // // 

var config = {
	container: "#OrganiseChart-simple",
};

var parent_node = {
	text: { name: "Parent no check" },
	HTMLid: 'parent',
	HTMLclass: 'light-gray'
};

var first_child = {
	parent: parent_node,
	text: { name: "First child" }
};

var second_child = {
	parent: parent_node,
	text: { name: "Second child" }
};

var simple_chart_config = [
	config, parent_node,
		first_child, second_child 
];
