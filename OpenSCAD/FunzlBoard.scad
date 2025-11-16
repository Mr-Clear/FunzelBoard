use <BananaJack.scad>;
use <Battery.scad>;
use <BatteryIndicator.scad>;
use <CableEntry.scad>;
use <ColorButton.scad>;
use <DipButton.scad>;
use <Fillet.scad>;
use <Led.scad>;
use <LedCap.scad>;
use <Pipe.scad>;
use <Poti.scad>;
use <PowerSwitch.scad>;
use <RockerSwitch.scad>;
use <Rounded_Cube.scad>;
use <Screws.scad>;
use <Slider.scad>;
use <SlideSwitch.scad>;
use <SmallButton.scad>;
use <Switch.scad>;
use <ToggleButton.scad>;
use <UsbCSocket.scad>;

fn_preview = 12;
fn_render = 100;

Show_Front = true;
Show_Back = true;
Show_Screws = true;
Screws_Always_Simple = true;
Show_Components = true;
Show_Text = true;
Show_Buzzer_Holder = true;
Show_Mainboard = true;

Board_Size = [180, 155, 30];
Edge_Size = 5;
Board_Color = "#840";
Wall_Thickness = 2;
Notch_Size = 1.0;
Notch_Backlash = 0.2;

Mainboard_Distance = 4.5;
Mainboard_Thickness = 1.6;

Black = "#222";
Metal_Color = "#999";
LED_Color = "#FFFA";
BananaJackColors = ["#22F", "#0F0", "#FF0"];
SliderColors = ["#F00", "#0F0", "#00F"];
SliderPositions = [1, 0, 1];
Color_Button_Colors = ["#F00", "#FF0", "#0F0", "#00F"];
Text_Color = "#0AF";
Mainboard_Color = "#0808";
Screw_Inserts_Color = "#A85";

Buzzer_Thickness = 0.14;
Buzzer_Diameter = 35;
Buzzer_Center_Diameter = 25;
Buzzer_Center_Thickness = 0.21;
Buzzer_Soldering_Point_Diameter = 3;
Buzzer_Soldering_Point_Height = 1;
Buzzer_Soldering_Point_Offsets = [9.5, 14.5];

Battery_Mount_Thickness = 3;

Screw_Hole_Wall_Thickness = 1.2;
Fillet_Size = 2;
Backlash = 0.2;

Led_Circle_Position = [100, 90];
Slider_Switch_Position = [30, 62];
Slider_Switch_Rotation = -50;
Rocker_Switch_Position = [110, 25];

Main_Screw_Positions = [[10, 10], [Board_Size[0] - 10, 10], [10, Board_Size[1] - 10], [Board_Size[0] - 10, Board_Size[1] - 10],
                        Led_Circle_Position, [78, 68], [20, 70], [140, 90], [90, 10], [70, 110]];

Main_Screw_Backlash = 0.2;
Main_Screw_Base_Wall_Thickness = 1.6;
Main_Screw_Head_Wall_Thickness = 1.6;
Main_Screw_Body_Wall_Thickness = 0.8;
Main_Screw_Base_Diameter = Screw_Definition_Main()[0] + 2 * Main_Screw_Body_Wall_Thickness;
Main_Screw_Head_Height = Screw_Definition_Main()[3] + Main_Screw_Backlash;

e = 0.001;

$fn = $preview ? fn_preview : fn_render;
LedZ = Board_Size[2] - Wall_Thickness - 1;

FunzlBoard();

module FunzlBoard() {
  if (Show_Front)
    difference() {
      Board_Front();
      ComponentsFront(true);
      ComponentsRight(true);
      ComponentsTop(true);
      ComponentsInner(true);
    }

  if (Show_Back) {
    Board_Back();
  }

  if (Show_Screws) {
    Main_Screws();
  }

  if (Show_Components) {
    ComponentsFront();
    ComponentsRight();
    ComponentsTop();
    ComponentsInner();
  }

  if (Show_Text) {
    color(Text_Color)
      translate([20, 115, Board_Size[2]]) {
        *translate([0, -2, 0])
          cube([139, 30, 1]);
        scale([1.35, 1.2, 1])
          linear_extrude(height=4)
            import("Funzlbredl.svg");
    }
  }

  if (Show_Buzzer_Holder)
    translate([Board_Size[0] / 2, Board_Size[1] - Edge_Size - Buzzer_Diameter / 2, Board_Size[2] - Wall_Thickness])
      Buzzer_Holder();

  if (Show_Mainboard)
    color(Mainboard_Color)
      translate([0, Board_Size[1], Board_Size[2] - Wall_Thickness - Mainboard_Distance - Mainboard_Thickness])
        import("../KiCad/FunzlBoard.stl", convexity=3);
}

module ComponentsFront(n = false) {
  // LED Circle
  translate([Led_Circle_Position[0], Led_Circle_Position[1], LedZ])
    LedCircle(16, 20, n);

  // 3 Toggle Switches
  translate([20, 25, 0]) {
    for (i = [0 : 2]) {
      translate([i * 20, 0, Board_Size[2] - Switch_Back_Length()])
        Switch("#D00", Metal_Color, 12, Wall_Thickness, n);
      for (y = [-1, 1])
        translate([i * 20, y * 14, LedZ])
          color(LED_Color)
            led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
    }
  }

  // 3 Way Switch
  translate([150, 50, 0]) {
    translate([0, 0, Board_Size[2] - Switch_Back_Length()])
      rotate([0, 0, 90])
        Switch("#D00", Metal_Color, 12, Wall_Thickness, n);
    for (x = [-1, 1])
      translate([x * 14, 0, LedZ])
        color(LED_Color)
          led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
  }

  // Sliders
  translate([138, 15, 0])
    for (i = [0 : 2]) {
      translate([i * 12, 5, Board_Size[2] + 0.5])
        Slider(SliderColors[i], Metal_Color, Black, Wall_Thickness, SliderPositions[i], n);
      translate([i * 12, 20, LedZ])
        color(LED_Color)
          led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
    }

  // Banana Jacks with LEDs
  translate([20, 100, 0])
    for (i = [0 : 2]) {
      translate([i * 18, 0, Board_Size[2]])
        BananaJack(BananaJackColors[i], [0.5, 0.5, 0.5], Wall_Thickness, false);
      translate([i * 18, -12, LedZ])
        color(LED_Color)
          led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
    }

  // Color Buttons
  translate([Led_Circle_Position[0], Led_Circle_Position[1], 0])
    for (i = [0 : len(Color_Button_Colors) - 1]) {
      rotate([0, 0, i * 45 - 157.5])
      translate([35, 0, Board_Size[2]])
        ColorButton(Color_Button_Colors[i]);
    }

  // Toggle Button
  translate([132.5, 103.5, Board_Size[2]])
    ToggleButton(Metal_Color);

  // LED Caps around Buttons
  translate([Led_Circle_Position[0], Led_Circle_Position[1], 0])
    for (i = [0 : 4]) {
      rotate([0, 0, i * 45 - 157.5])
      translate([47, 0, LedZ])
        color(LED_Color)
          led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
    }

  // Small Button
  translate([50, 55, Board_Size[2]])
    SmallButton(Black);
  translate([50, 45, LedZ])
    color(LED_Color)
      led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);

  // Potentiometer
  translate([83, 25, Board_Size[2]])
    Poti("#A83", Metal_Color, Wall_Thickness);

  // Rocker Switch
  translate([Rocker_Switch_Position[0], Rocker_Switch_Position[1], 0]) {
    translate([0, 0, Board_Size[2]])
      rotate([0, 0, -90])
        RockerSwitch(Black, Metal_Color, n);
    for(x = [-1, 1])
      for (y = [-1, 1])
        translate([x * 10, y * 10, LedZ])
          color(LED_Color)
            led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
    if (!n)
      for (x = [-1, 1]) {
        translate([0, Rocker_Switch_Screw_Hole_Distance() / 2 * x, Board_Size[2] - Wall_Thickness - e])
          Screw_Insert_From_Definition(Screw_Insert_Definition_Rocker_Switch(), Screw_Inserts_Color, Screws_Always_Simple);
        translate([0, Rocker_Switch_Screw_Hole_Distance() / 2 * x, Board_Size[2] + Rocker_Switch_Plate_Thickness() + e])
          Screw_Cylinder_Hex_From_Definition(Screw_Definition_Rocker_Switch(), Metal_Color, Screws_Always_Simple);
      }
  }

  // Slider Switch
  translate([Slider_Switch_Position[0], Slider_Switch_Position[1], 0])
    rotate([0, 0, Slider_Switch_Rotation]) {
      translate([0, 0, Board_Size[2]])
        Slide_Switch(Black, Metal_Color, n);
      for (x = [-1, 1])
        translate([0, x * 14, LedZ])
          color(LED_Color)
            led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
      if (!n)
        for (x = [-1, 1]) {
          translate([0, x * Slide_Switch_Screw_Hole_Distance() / 2, Board_Size[2] - Wall_Thickness - e])
            Screw_Insert_From_Definition(Screw_Insert_Definition_Slide_Switch(), Screw_Inserts_Color, Screws_Always_Simple);
          translate([0, x * Slide_Switch_Screw_Hole_Distance() / 2, Board_Size[2] + Slide_Switch_Plate_Thickness() + e])
            Screw_Cylinder_Hex_From_Definition(Screw_Definition_Slide_Switch(), Black, Screws_Always_Simple);
        }
    }

  // Battery Indicator
  translate([158, 90, Board_Size[2] + e])
      BatteryIndicator(Metal_Color, n);

  // DIP Button
  translate([158, 65, Board_Size[2] - Wall_Thickness - 0.5])
    DipButton("#222", Metal_Color, n);
}

module ComponentsTop(n = false) {
  // Cable Entry
  translate([38, Board_Size[1], Board_Size[2] / 2])
    rotate([-90, 0, 0])
      CableEntry(Black, Wall_Thickness);
}

module ComponentsRight(n = false) {
  // Battery LED
  translate([Board_Size[0] - 6, 120, Board_Size[2] / 2])
    rotate([90, 0, 90])
      Led("#FF0");

  // USB-C Socket
  translate([Board_Size[0], 108, Board_Size[2] / 2])
    rotate([90, 0, 90])
      USB_C_Socket(Black, Metal_Color, n);

  // Charge LED
  translate([Board_Size[0] - 6, 96, Board_Size[2] / 2])
    rotate([90, 0, 90])
      Led("#F00");

  // Power Switch
  translate([Board_Size[0], 84, Board_Size[2] / 2])
    rotate([90, 180, 90])
      PowerSwitch(Black, Metal_Color);

  // Status LED
  translate([Board_Size[0] - 6, 72, Board_Size[2] / 2])
    rotate([90, 0, 90])
      Led("#00F");
}

module ComponentsInner(n = false) {
  // Battery Holder
  translate([Board_Size[0] / 2, Board_Size[1] - Edge_Size - Buzzer_Diameter / 2, Board_Size[2] - Wall_Thickness - Battery_Mount_Thickness]) {
    rotate([180, 0, 0])
      Battery("#222", "#2D42", false);
    for (x = [-1, 1])
      translate([x * (Battery_Mount_Holes_Distance()) / 2, 0, -Battery_Case_Thickness_Bottom()])
        rotate([180, 0, 0])
          Screw_Sunken_Hex_From_Definition(Screw_Definition_Battery(), Black, Screws_Always_Simple);

    if (!n)
      for (x = [-1, 1])
        translate([x * (Battery_Mount_Holes_Distance()) / 2, 0, Screw_Insert_Definition_Battery()[1]])
          Screw_Insert_From_Definition(Screw_Insert_Definition_Battery(), Screw_Inserts_Color, Screws_Always_Simple);
  }

  // Buzzer
  for (i = [-1 : 1])
    translate([Board_Size[0] / 2 + i * 60, Board_Size[1] - Edge_Size - Buzzer_Diameter / 2, Board_Size[2] - Wall_Thickness - Buzzer_Thickness]) {
      Buzzer(n);
    }
}

module Buzzer(negative = false) {
  color("#880")
    cylinder(h = Buzzer_Thickness, d = Buzzer_Diameter);
  color("#CCC")
    translate([0, 0, -Buzzer_Center_Thickness])
      cylinder(h = Buzzer_Center_Thickness, d = Buzzer_Center_Diameter);
  color(Metal_Color)
    for (offset = Buzzer_Soldering_Point_Offsets)
      translate([0, offset, -Buzzer_Soldering_Point_Height])
        cylinder(h = Buzzer_Soldering_Point_Height, d = negative ? Buzzer_Soldering_Point_Diameter + Backlash : Buzzer_Soldering_Point_Diameter);
  if (negative) {
    cylinder(Wall_Thickness + Buzzer_Thickness + e, d = 6);
  }
}

module LedCircle(num, radius, n) {
  for (i = [0 : num - 1])
    rotate([0, 0, i * 360 / num])
      translate([radius, 0, 0])
        color(LED_Color)
          led_cap(negative=n, color=LED_Color, metal_color=Metal_Color);
}

module Board() {
  color(Board_Color)
    difference() {
      Rounded_Cube(Board_Size, Edge_Size);
      translate([Wall_Thickness, Wall_Thickness, Wall_Thickness])
        Rounded_Cube([Board_Size[0] - Wall_Thickness * 2, Board_Size[1] - Wall_Thickness * 2, Board_Size[2] - Wall_Thickness * 2],
                     Edge_Size - Wall_Thickness);
    }
}

module Board_Front() {
  color(Board_Color) {
    intersection() {
      Board();
      translate([-e / 2, -e / 2, Edge_Size + .05])
        cube([Board_Size[0] + e, Board_Size[1] + e, Board_Size[2]]);
    }
    Notch(Notch_Size);

    // Battery Mount
    translate([Board_Size[0] / 2, Board_Size[1] - Edge_Size - Buzzer_Diameter / 2, Board_Size[2] - Wall_Thickness]) {
      for (x = [-1, 1])
        translate([x * (Battery_Mount_Holes_Distance()) / 2, 0, -Battery_Mount_Thickness]) {
          Pipe(Battery_Mount_Thickness, Screw_Insert_Definition_Battery()[2] + Screw_Hole_Wall_Thickness * 2, Screw_Insert_Definition_Battery()[2] / 2);
          rotate([180, 0, 0])
            translate([0, 0, -Battery_Mount_Thickness])
            FilletCylinder(Screw_Insert_Definition_Battery()[2] + Screw_Hole_Wall_Thickness * 2, Fillet_Size, true);
        }
    }

    // Main Screw Holes
    for (pos = Main_Screw_Positions) {
      translate([pos[0], pos[1], Board_Size[2] - Wall_Thickness - Mainboard_Distance]) {
        difference() {
          cylinder(Mainboard_Distance, d = Main_Screw_Base_Diameter + 2 * Main_Screw_Base_Wall_Thickness);
          translate([0, 0, -e])
            cylinder(Screw_Insert_Definition_Main()[1], d = Screw_Insert_Definition_Main()[2]);
        }
        rotate([180, 0, 0])
          translate([0, 0, -Mainboard_Distance - e])
            FilletCylinder(Main_Screw_Base_Diameter / 2 + Main_Screw_Base_Wall_Thickness, Fillet_Size, true);
      }
    }

    // Rocker Switch Screw Holes
    Rocker_Switch_Screw_Nut_Height = 3;
    Rocker_Switch_Screw_Nut_Diameter = 4.0;
    for (x = [-1, 1])
      translate([Rocker_Switch_Position[0], Rocker_Switch_Position[1], Board_Size[2] - Wall_Thickness])
        rotate([0, 0, -90])
          translate([x * (Rocker_Switch_Screw_Hole_Distance()) / 2, 0, -Rocker_Switch_Screw_Nut_Height]) {
            difference() {
              cylinder(h = Rocker_Switch_Screw_Nut_Height + e, d = Rocker_Switch_Screw_Nut_Diameter + 2 * Screw_Hole_Wall_Thickness);
              translate([0, 0, -e])
                cylinder(h = Rocker_Switch_Screw_Nut_Height + e, d = Rocker_Switch_Screw_Nut_Diameter);
            }
            rotate([180, 0, 0])
              translate([0, 0, -Rocker_Switch_Screw_Nut_Height])
                FilletCylinder(Rocker_Switch_Screw_Nut_Diameter / 2 + Screw_Hole_Wall_Thickness, Rocker_Switch_Screw_Nut_Height);
        }

    // Slider Switch Screw Holes
    for (y = [-1, 1])
      translate([Slider_Switch_Position[0], Slider_Switch_Position[1], Board_Size[2] - Wall_Thickness])
        rotate([0, 0, Slider_Switch_Rotation])
          translate([0, y * (Slide_Switch_Screw_Hole_Distance()) / 2, -Screw_Insert_Definition_Slide_Switch()[1]]) {
            difference() {
              cylinder(h = Screw_Insert_Definition_Slide_Switch()[1] + e, d = Screw_Insert_Definition_Slide_Switch()[2] + 2 * Screw_Hole_Wall_Thickness);
              translate([0, 0, -e])
                cylinder(h = Screw_Insert_Definition_Slide_Switch()[1] + e, d = Screw_Insert_Definition_Slide_Switch()[2]);
            }
            rotate([180, 0, 0])
              translate([0, 0, -Screw_Insert_Definition_Slide_Switch()[1]])
                FilletCylinder(Screw_Insert_Definition_Slide_Switch()[2] / 2 + Screw_Hole_Wall_Thickness, Screw_Insert_Definition_Slide_Switch()[1]);
        }
  }

  // Main Screw Inserts
  if (Show_Screws)
    for (pos = Main_Screw_Positions)
      translate([pos[0], pos[1], Board_Size[2] - Wall_Thickness - Mainboard_Distance + Screw_Insert_Definition_Main()[1] - e])
        Screw_Insert_From_Definition(Screw_Insert_Definition_Main(), Screw_Inserts_Color, Screws_Always_Simple);
}

module Board_Back() {
  color(Board_Color)
    difference() {
      union() {
        intersection() {
          Board();
          cube([Board_Size[0] + e, Board_Size[1] + e, Edge_Size - .05]);
        }
        // Main Screws
        for (pos = Main_Screw_Positions) {
          translate([pos[0], pos[1], 0]) {
            cylinder(Board_Size[2] - Mainboard_Distance - Mainboard_Thickness - Wall_Thickness,
                     d = Screw_Definition_Main()[0] + Main_Screw_Body_Wall_Thickness * 2);
            translate([0, 0, Wall_Thickness])
              FilletCylinder(Screw_Definition_Main()[0] / 2 + Main_Screw_Body_Wall_Thickness, Main_Screw_Head_Height + Main_Screw_Head_Wall_Thickness + Main_Screw_Base_Wall_Thickness);
          }
        }
      }
      Notch(Notch_Size + Notch_Backlash);

      // Main Screws
      for (pos = Main_Screw_Positions) {
        translate([pos[0], pos[1], -e]) {
          cylinder(Board_Size[2], d = Screw_Definition_Main()[0] + Main_Screw_Backlash * 2);
          cylinder(Main_Screw_Head_Height, d = Screw_Definition_Main()[2] + Main_Screw_Backlash * 2);
        }
      }
    }
}

module Main_Screws() {
  for (pos = Main_Screw_Positions)
    translate([pos[0], pos[1], Screw_Definition_Main()[3]])
      rotate([180, 0, 0])
        Screw_Cylinder_Hex_From_Definition(Screw_Definition_Main(), Black, Screws_Always_Simple);
}

module Notch(size) {
  translate([Wall_Thickness / 2, Edge_Size, Edge_Size])
    rotate([-90, 0, 0])
      cylinder(h = Board_Size[1] - 2 * Edge_Size, d = size);
  translate([Board_Size[0] - Wall_Thickness / 2, Edge_Size, Edge_Size])
    rotate([-90, 0, 0])
      cylinder(h = Board_Size[1] - 2 * Edge_Size, d = size);
  translate([Edge_Size, Wall_Thickness / 2, Edge_Size])
    rotate([0, 90, 0])
      cylinder(h = Board_Size[0] - 2 * Edge_Size, d = size);
  translate([Edge_Size, Board_Size[1] - Wall_Thickness / 2, Edge_Size])
    rotate([0, 90, 0])
      cylinder(h = Board_Size[0] - 2 * Edge_Size, d = size);
  translate([Edge_Size, Edge_Size, Edge_Size])
    rotate_extrude(90, 180)
      translate([Edge_Size - Wall_Thickness / 2, 0])
        circle(d = size);
  translate([Edge_Size, Board_Size[1] - Edge_Size, Edge_Size])
    rotate_extrude(90, 90)
      translate([Edge_Size - Wall_Thickness / 2, 0])
        circle(d = size);
  translate([Board_Size[0] - Edge_Size, Board_Size[1] - Edge_Size, Edge_Size])
    rotate_extrude(90, 0)
      translate([Edge_Size - Wall_Thickness / 2, 0])
        circle(d = size);
  translate([Board_Size[0] - Edge_Size, Edge_Size, Edge_Size])
    rotate_extrude(90, 270)
      translate([Edge_Size - Wall_Thickness / 2, 0])
        circle(d = size);
}

module Buzzer_Holder() {
  color(Black) {
    for (x = [-1, 0, 1])
      difference() {
        translate([x * 60, 0, -Battery_Mount_Thickness])
          Pipe(Battery_Mount_Thickness - e, Buzzer_Diameter / 2 - Backlash, Buzzer_Center_Diameter / 2 + Backlash);
        translate([0, Buzzer_Soldering_Point_Offsets[1], 0])
          scale([Buzzer_Soldering_Point_Diameter, Buzzer_Soldering_Point_Diameter, Buzzer_Soldering_Point_Height])
            sphere(1);
      }
    for (x = [-1, 1], y = [-1, 1])
      translate([x * 30, y * (Screw_Insert_Definition_Battery()[2] + Screw_Hole_Wall_Thickness * 2 * Fillet_Size + 3), -Battery_Mount_Thickness / 2])
        cube([41, 6, Battery_Mount_Thickness - e], center=true);
  }
}
