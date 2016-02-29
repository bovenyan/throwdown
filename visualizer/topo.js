var topo = function (p) {
	// socket connect to server
	var socket;

	// elements in the topology
	var nodes = [];
	var links = [];
	var lsps = [];

	// color schema
	var colors = [
	'rgba(0,64,16,0.7)',
	'rgba(0,18,229,0.7)',
	'rgba(127,1,0,0.7)',
	'rgba(255,0,170,0.7)',
	'rgba(255,0,0,0.7)',
	'rgba(225,118,0,0.7)',
	'rgba(101,0,127,0.7)',
	'rgba(0,125,255,0.7)'
	];

	// counter for northstar update
	var northStarUpdate = 0;
	var redisUpdate = 0;

	// size of canvas
	var width;
	var height;

	// array of buttons
	var buttons = [];
	var west_2_east = [];
	var east_2_west = [];

	// mouse press event handler
	function onMousePressed() {
		for (var i = 0; i < buttons.length; i++) {
			if (p.mouseX > buttons[i].l && p.mouseX < buttons[i].r && p.mouseY > buttons[i].u && p.mouseY < buttons[i].b) {
				if (buttons[i].show) {
					buttons[i].show = false;
				} else {
					buttons[i].show = true;
				}
			}
		}

		if (p.mouseX > east_2_west.l && p.mouseX < east_2_west.r && p.mouseY > east_2_west.u && p.mouseY < east_2_west.b) {
			if (east_2_west.show) {
				east_2_west.show = false;
				for (var i = 0; i < 4; i++) {
					buttons[i].show = false;
				}
			} else {
				east_2_west.show = true;
				for (var i = 0; i < 4; i++) {
					buttons[i].show = true;
				}
			}
		}

		if (p.mouseX > west_2_east.l && p.mouseX < west_2_east.r && p.mouseY > west_2_east.u && p.mouseY < west_2_east.b) {
			if (west_2_east.show) {
				west_2_east.show = false;
				for (var i = 4; i < 8; i++) {
					buttons[i].show = false;
				}
			} else {
				west_2_east.show = true;
				for (var i = 4; i < 8; i++) {
					buttons[i].show = true;
				}
			}
		}
	}

	function arrow(x1, y1, x2, y2, length) {
		var angle = p.atan2(y2-y1, x2-x1);
		// console.log(angle + " from (" + x1 + "," + y1 + ") to (" + x2 + "," + y2 + ")");
		p.push();
		p.translate(x1,y1);
		p.rotate(angle);
		p.beginShape();
		p.vertex(0,-4);
		p.vertex(5*length,-3);
		p.vertex(5*length,-9);
		p.vertex(9*length,0);
		p.vertex(5*length,9);
		p.vertex(5*length,3);
		p.vertex(0,4);
		p.endShape(p.CLOSE);
		p.pop();
	}

	// Visualization of topology in a Wide Area Network
	p.setup = function () {
		// console.log('in topo');
		// creat canvas
		const canvasHolder = p.select('#topo-main'),
		      width = canvasHolder.width,
		      height = canvasHolder.height;
		// console.log(width);
		// console.log(height);
		canvas = p.createCanvas(width, height).parent('topo-main');
		canvas.mousePressed(onMousePressed);

		// set frame rate as 25 fps
		p.frameRate(25);

		// Add buttons
		for (var i = 0; i < 4; i++) {
			var button = {
				l: width*0.82,
				r: width*0.82+width*0.07,
				u: height*0.3+height*0.2*i,
				b: height*0.3+height*0.2*i+height*0.1,
				show: false
			}
			buttons.push(button);
		}

		for (var i = 0; i < 4; i++) {
			var button = {
				l: width*0.91,
				r: width*0.91+width*0.07,
				u: height*0.3+height*0.2*i,
				b: height*0.3+height*0.2*i+height*0.1,
				show: false
			}
			buttons.push(button);
		}

		east_2_west = {
			l: width*0.82,
			r: width*0.82+width*0.07,
			u: height*0.1,
			b: height*0.2,
			show: false
		}

		west_2_east = {
			l: width*0.91,
			r: width*0.91+width*0.07,
			u: height*0.1,
			b: height*0.2,
			show: false
		}

		// Establish socket between browser and server
		socket = io.connect('http://localhost:8080');
		socket.emit('northstar');

		socket.on('welcome', function(data) {
			// console.log(data.welcome);
		});

		socket.on('nodes', function(data) {
			nodes = data;
			for (var i = 0; i < 8; i++) {
				nodes[i].x = p.map(nodes[i].longtitude, -130, -70, 0, width*0.8);
				nodes[i].y = p.map(-nodes[i].latitude, -45, -25, 0, height);
			}
			// console.log(nodes);
			// console.log('New nodes information received');
		});

		socket.on('links', function(data) {
			// console.log(data);
			links = data;
			// console.log('New links information received');
		})

		socket.on('lsps', function(data) {
			// console.log(data);
			lsps = data
			// console.log('New LSPs information received');
		})
	}

	p.draw = function () {

		// counting whether to update northstar informations && redis information
		if (nodes.length == 8 && links.length == 15 && lsps.length == 8) {
			if (northStarUpdate < 75) {
				northStarUpdate++;
			} else {
				socket.emit('northstar_update');
				northStarUpdate = 0;
			}

			if (redisUpdate < 750) {
				redisUpdate++;
			} else {
				socket.emit('redis_update');
				redisUpdate = 0;
			}
		}

		p.background(255);

		// Links
		for (var i = 0; i < links.length; i++) {
			// console.log('drawing links');
			// console.log(links[i]);
			p.stroke(230,230,230);
			p.strokeWeight(5);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y+5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y+5);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y-5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y-5);
			p.stroke('rgba(0,0,0,0.5)');
			p.strokeWeight(5*links[i].utilA2Z);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y+5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y+5);
			p.fill('rgba(0,0,0,'+links[i].utilA2Z+')');
			// p.fill('rgba(0,0,0,1)');
			p.stroke(0);
			arrow(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y+5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y+5, 10);
			p.stroke('rgba(0,0,0,0.5)');
			p.strokeWeight(5*links[i].utilZ2A);
			p.line(nodes[links[i].endA-1].x, nodes[links[i].endA-1].y-5, nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y-5);
			p.fill('rgba(0,0,0,'+links[i].utilZ2A+')');
			p.stroke(0);
			arrow(nodes[links[i].endZ-1].x, nodes[links[i].endZ-1].y-5, nodes[links[i].endA-1].x, nodes[links[i].endA-1].y-5, 10);
		}

		// Nodes
		p.stroke(50);
		p.strokeWeight(1);
		for (var i = 0; i < nodes.length; i++) {
			p.fill(100);
			p.ellipse(nodes[i].x, nodes[i].y, 25, 25);
			p.textSize(24);
			p.fill(0, 102, 153);
			p.text(nodes[i].name, nodes[i].x, nodes[i].y+25);
			// console.log(nodes);
		}

		// LSPs
		for (var i = 0; i < lsps.length; i++) {
			// console.log(colors);
			if (buttons[i].show) {
				for (var j = 0; j < lsps[i].links.length; j++) {
					p.stroke(colors[i]);
					p.strokeWeight(4);
					p.line(
						nodes[links[lsps[i].links[j]].endA-1].x,
						nodes[links[lsps[i].links[j]].endA-1].y+i*2,
						nodes[links[lsps[i].links[j]].endZ-1].x,
						nodes[links[lsps[i].links[j]].endZ-1].y+i*2);
				}
			}

			p.stroke(0);
			p.strokeWeight(1);
			if (buttons[i].show) {
				p.fill(colors[i]);
			} else {
				p.fill(255);
			}

			var width = p.width;
			var height = p.height;
			var w = width*0.07;
			var h = height*0.1;
			if (i < 4) {
				p.rect(width*0.82, height*0.3+height*0.2*i, w, h);
				p.textSize(h*0.2);
				p.fill(0);
				p.strokeWeight(1);
				p.text(lsps[i].name, width*0.82, height*0.3+height*0.2*i, w, h);
			}
			if (i >= 4) {
				p.rect(width*0.91, height*0.3+height*0.2*(i-4), w, h);
				p.textSize(h*0.2);
				p.fill(0);
				p.strokeWeight(1);
				p.text(lsps[i].name, width*0.91, height*0.3+height*0.2*(i-4), w, h);
			}
		}

		p.stroke(0);
		p.strokeWeight(1);
		p.fill(255);
		p.rect(east_2_west.l, east_2_west.u, east_2_west.r-east_2_west.l, east_2_west.b-east_2_west.u);
		p.noStroke();
		p.strokeWeight(2);
		p.fill(0);
		p.text("East to West", east_2_west.l, east_2_west.u, east_2_west.r-east_2_west.l, east_2_west.b-east_2_west.u);

		p.stroke(0);
		p.strokeWeight(1);
		p.fill(255);
		p.rect(west_2_east.l, west_2_east.u, west_2_east.r-west_2_east.l, west_2_east.b-west_2_east.u);
		p.noStroke();
		p.strokeWeight(2);
		p.fill(0);
		p.text("West to East", west_2_east.l, west_2_east.u, west_2_east.r-west_2_east.l, west_2_east.b-west_2_east.u);
	}
}
