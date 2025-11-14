$fn = 100;

LED_Size = [5.4, 5.4, 1.5];
Cap_Height = 9;
Cap_Diameter = 6;
Foot_Diameter = 8;
Foot_Height = 2;

Hollow_Height = Cap_Height - 0.5;
Hollow_Diameter = 4.5;

Grid_Distance = 8.3;
Grid = [3, 3];
capa_size = [5, 2, 0.8];

Sleeve_Height = 5;
Sleeve_Outer = 3.9;
Sleeve_Inner = 3.5;

e = 0.001;

led_cap();

*difference() {
  union() {
    for (y = [1:Grid[1]])
      for (x = [1:Grid[0]])
        translate([(x - 1) * Grid_Distance, (y - 1) * Grid_Distance, 0])
          led_cap(LED_Size,
                  Cap_Height,
                  Cap_Diameter,
                  Foot_Diameter,
                  Foot_Height,
                  Hollow_Height,
                  Hollow_Diameter);
    hull()
      for (y = [1:Grid[1]])
        for (x = [1:Grid[0]])
          translate([(x - 1) * Grid_Distance, (y - 1) * Grid_Distance, 0])
            cylinder(Foot_Height, d = Foot_Diameter);
  }
  for (y = [1:Grid[1]])
    for (x = [0:Grid[0]]) {
      translate([(x - 0.5) * Grid_Distance - capa_size[0] / 2, (y - 1) * Grid_Distance - capa_size[1] / 2, -e])
        cube(capa_size);
      translate([(x - 1) * Grid_Distance, (y - 1) * Grid_Distance, -e]) {
        translate([-LED_Size[0] / 2, -LED_Size[1] / 2, 0])
          cube(LED_Size);
        cylinder(Hollow_Height - Hollow_Diameter / 2, d = Hollow_Diameter);
        translate([0, 0, Hollow_Height - Hollow_Diameter / 2])
          sphere(d = Hollow_Diameter);
      }
    }
}

module led_cap(led_size = LED_Size,
               cap_height = Cap_Height,
               cap_diameter = Cap_Diameter,
               foot_diameter = Foot_Diameter,
               foot_height = Foot_Height,
               hollow_height = Hollow_Height,
               hollow_diameter = Hollow_Diameter,
               negative = false,
               backlash = 0.4,
               color = "#FFFA",
               metal_color = "#999") {
  b = negative ? backlash : 0;
  bc = negative ? backlash * 10 : 0;
  color(color) {
    difference() {
      union() {
        translate([0, 0, -bc]) {
          cylinder(cap_height - cap_diameter / 2 + bc, d = cap_diameter + b);
          translate([0, 0, cap_height - cap_diameter / 2])
            sphere(d = cap_diameter + b);
          cylinder(foot_height + bc, d = foot_diameter + b);
        }
      }
      if (!negative) {
        translate([0, 0, -e]) {
          translate([-led_size[0] / 2, -led_size[1] / 2, 0])
            cube(led_size);
          cylinder(hollow_height - hollow_diameter / 2, d = hollow_diameter);
          translate([0, 0, hollow_height - hollow_diameter / 2])
            sphere(d = hollow_diameter);
        }
        translate([0, 0, -Cap_Diameter / 2])
          cylinder(Cap_Diameter / 2 + e, d = Cap_Diameter);
      }
    }
  }
  if (!negative)
    color(metal_color) {
      translate([0, 0, LED_Size[2]])
        difference() {
          cylinder(Sleeve_Height, d = Sleeve_Outer);
          translate([0, 0, -e/2])
            cylinder(Sleeve_Height + e, d = Sleeve_Inner);
        }
    }
}

