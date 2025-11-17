$fn = 100;

Board_Size = [33.3, 16.8, 1.2];
Pin_Size = [0.7, 0.7, 5.6];
Pin_Sunken = 1.6;
Hole_Size = 1.2;
Pin_Positions = [
  [-15.0, -6.75],
  [-15.0,  6.75],
  [ -4.1,  6.75],
  [  4.1,  6.75],
  [ 15.0,  6.75],
  [ 15.0, -6.75],
  [-11.4,  0.00],
  [-11.4, -2.54],
  [-11.4,  2.54],
];
Components = [
  [[5.2, 5.6, 4.5], [  9.4,  1.2]],
  [[4.7, 3.8, 1.0], [  3.1,  0.0]],
  [[2.0, 2.9, 1.2], [ -9.8,  6.6]],
  [[1.3, 2.0, 1.3], [ 15.0,  0.0]],
  [[1.3, 2.0, 1.3], [-15.0,  0.0]],
  [[1.3, 2.0, 1.3], [  7.9, -5.1]],
  [[1.3, 2.0, 1.3], [ 10.5, -5.1]],
  [[1.3, 2.8, 0.9], [-10.3, -6.3]],
];

e = 0.001;

BatteryManagement("#080", "#888", "#222");

function BatteryManagement_Distance(bainboard_thickness) = Pin_Size.z - Pin_Sunken * 1.5 - bainboard_thickness;

module BatteryManagement(board_color, metal_color, black) {
  difference() {
    color(board_color)
      cube(Board_Size, center = true);

    for (pos = Pin_Positions)
      translate(pos)
        cylinder(Board_Size.z + e, d = Hole_Size, center = true);
  }

  color(metal_color) {
    for (pos = Pin_Positions)
      translate([pos.x, pos.y, Pin_Size.z / 2 - Pin_Sunken])
        cube([Pin_Size.x, Pin_Size.y, Pin_Size.z + e], center = true);
  }

  color(black) {
    for (i = [0 : len(Components) - 1]) {
      component_size = Components[i][0];
      component_position = Components[i][1];
      if (component_size != [0, 0, 0])
        translate([component_position.x, component_position.y, -Board_Size.z / 2 - component_size.z / 2])
          cube(component_size, center = true);
    }
  }
}
