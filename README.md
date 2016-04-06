# rpipin
Homebrew pinball project for the Raspberry Pi

This is a personal project created by a true amateur, but also created with love (or something similar). The point of this is not to create something production worthy, but to satisfy the DIY itch. I want to create a pinball table using what I consider to be only my ideas, so I'm trying to limit my exposure to the rest of the world's pinball development so I can have a design that I made myself.

Obviously there are things I will want to source pre-made, especially in the mechanical department, but I'm going to attempt to homebrew this all the way.

So far, I have the following designs completed:
  Software:  
  - Main program game loop
  - Sound and music
  - Input detection
  - Output activation and timed/sequenced event support
  - Addressable LED control
  - Magnetic tilt sensor (Thought this was an accelerometer, so the solenoids basically ruin this)
  - Control of paddles/hardware from terminal or button
  Hardware:
  - i2c input/output board
    - 5VDC inputs, built-in pullup resistors, inputs activate on connection to ground
    - Up to 48VDC outputs, maximum about 8A each output 8 outputs (up to 3 active at once)
    - Address can be changed with dip switch
    - Fused for 8A slowblow
    - Absolutely, positively requires flyback diodes.
  - WS2812 Knockoff LED Chain
    - Controlled by PWM output from RPi. Consider using separate control board for longer LED runs.
  - 48VDC @ 8.3A Power Supply
  - 5VDC @ 10A Power Supply
  - Various pinball solenoids and assemblies
  - Servo controller and servos
  - Laser diodes
  - Loser camera
    
Future plans:
  - Need a theme. This should have been thought of already.
  - Whitewood design
  - Need to determine how to use LED marquee or something for main display (not too keen on LCD)
  - High scores accessible from net
