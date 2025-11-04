Stick_Out_Edge_Depth = 1.5;
Stick_Out_Edge_Length = 15.5;
Stick_Out_Edge_Width = 9.4;

Stick_Out_End_Depth = 2.1;
Stick_Out_End_Length = 11.3;
Stick_Out_End_Width = 5.3;
Stick_Out_End_Edge_Radius = 1.2;

Hole_Length = 8.2;
Hole_Width = 2.5;
Hole_Depth = 5.1;

Metal_Thickness = 0.2;

Plastic_Hole_Length = Hole_Length + Metal_Thickness * 2;
Plastic_Hole_Width = Hole_Width + Metal_Thickness * 2;

Plate_Width = 6.3;
Plate_Thickness = 0.6;

Back_Length = 12.6;
Back_Width = 5.4;
Back_Depth = 8.8;
Back_Edge = 1.1;
Back_Cutout = 0.4;

Clamp_Height = 2.8;
Clamp_Width = 1;

Cable_Width = 1.4;
Cable_Offset = 2.3;
Cable_Length = 5;

Wire_Width = 0.6;
Wire_Length = 1;

Back_Polygon = [[-Back_Length / 2, -Back_Width / 2 + Back_Edge],
                [-Back_Length / 2 + Back_Edge, -Back_Width / 2],
                [-Back_Cutout, -Back_Width / 2],
                [-Back_Cutout, -Back_Width / 2 + Back_Cutout],
                [Back_Cutout, -Back_Width / 2 + Back_Cutout],
                [Back_Cutout, -Back_Width / 2],
                [Back_Length / 2 - Back_Edge, -Back_Width / 2],
                [Back_Length / 2, -Back_Width / 2 + Back_Edge],
                [Back_Length / 2, Back_Width / 2 - Back_Edge],
                [Back_Length / 2 - Back_Edge, Back_Width / 2],
                [-Back_Cutout, Back_Width / 2],
                [-Back_Cutout, Back_Width / 2 - Back_Cutout],
                [Back_Cutout, Back_Width / 2 - Back_Cutout],
                [Back_Cutout, Back_Width / 2],
                [-Back_Length / 2 + Back_Edge, Back_Width / 2],
                [-Back_Length / 2, Back_Width / 2 - Back_Edge]];

e = 0.001;

USB_C_Socket("#111", "#AAA");

module USB_C_Socket(color, metal_color, negative = false) {
    if (negative) {
        color(color)
            translate([0, 0, -Back_Depth])
                linear_extrude(Back_Depth, convexity = 2)
                    polygon(Back_Polygon);

        for (x = [-1, 1])
            translate([x * (Back_Length + Clamp_Width - e) / 2, 0, -Back_Depth / 2])
                cube([Clamp_Width, Clamp_Height, Back_Depth], center = true);
    } else {
        color(color) {
            difference() {
                union() {
                    hull() {
                        for (x = [-1, 1]) {
                            translate([x * (Stick_Out_Edge_Length - Stick_Out_Edge_Width) / 2, 0, 0]) {
                                cylinder(Stick_Out_Edge_Depth, d = Stick_Out_Edge_Width);
                            }
                            for (y = [-1, 1]) {
                                translate([x * (Stick_Out_End_Length - Stick_Out_End_Edge_Radius) / 2,
                                        y * (Stick_Out_End_Width - Stick_Out_End_Edge_Radius) / 2,
                                        Stick_Out_End_Depth]) {
                                    cylinder(e, d = Stick_Out_End_Edge_Radius);
                                }
                            }
                        }
                    }
                    translate([0, 0, -Back_Depth])
                        linear_extrude(Back_Depth, convexity = 2)
                            polygon(Back_Polygon);
                }
                hull() {
                    for (x = [-1, 1]) {
                        translate([x * (Plastic_Hole_Length - Plastic_Hole_Width) / 2, 0, Stick_Out_End_Depth - Plastic_Hole_Length + e / 2]) {
                            cylinder(Plastic_Hole_Length + e, d = Plastic_Hole_Width);
                        }
                    }
                }
            }

            translate([0, 0, Stick_Out_End_Depth - Plastic_Hole_Length / 2])
                cube([Plate_Width, Plate_Thickness, Plastic_Hole_Length], center = true);

            for (x = [-1, 1])
                translate([x * (Back_Length + Clamp_Width - e) / 2, 0, -Back_Depth / 2])
                    cube([Clamp_Width, Clamp_Height, Back_Depth], center = true);
        }

        color(metal_color)
            difference() {
                hull()
                    for (x = [-1, 1])
                        translate([x * (Plastic_Hole_Length - Plastic_Hole_Width) / 2, 0, Stick_Out_End_Depth - Hole_Depth + e / 2])
                            cylinder(Hole_Depth, d = Plastic_Hole_Width);
                translate([0, 0, e])
                    hull()
                        for (x = [-1, 1])
                            translate([x * (Hole_Length - Hole_Width) / 2, 0, Stick_Out_End_Depth - Hole_Depth - e])
                                cylinder(Hole_Depth + e * 2, d = Hole_Width);
            }

        for (cable = [[-1, "#F00"], [1, "#111"]]) {
            translate([cable[0] * Cable_Offset, 0, -Back_Depth - Cable_Length]) {
                color(cable[1])
                    cylinder(Cable_Length, d = Cable_Width);
                translate([0, 0, -Wire_Length])
                    color(metal_color)
                        cylinder(Wire_Length, d = Wire_Width);
            }
        }
    }
}

function USB_C_Socket_Dimensions() = [Stick_Out_Edge_Length, Stick_Out_Edge_Width, Stick_Out_Edge_Depth];
