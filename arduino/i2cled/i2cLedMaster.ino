#include <Adafruit_NeoPixel.h>
#include <Wire.h>

#ifdef __AVR__
  #include <avr/power.h>
#endif

// Disables i2c pullup resistors. Disable this if you don't have any on the i2c bus.
// It is recommended to use external pullups based on the capacitance of your i2c bus.
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif

// PIN is the digital output pin used for LED control
// NUM_LEDS is the number of LEDS on the string
#define PIN 3
#define NUM_LEDS 29

#define I2C_ADDRESS 0x10            // Slave i2c address

// Command codes. Set these to whatever you want, just make sure to update the master as well
// 0x01 to 0xFF are available

//Permanent Set
#define SET_SINGLE_COLOR      0x15

//Temporary Set
#define COLOR_WIPE            0x20

//Long Animations
#define RAINBOW               0x50
#define RAINBOW_CYCLE         0x51
#define THEATER_CHASE         0x52
#define THEATER_CHASE_RAINBOW 0x53

//Short Animations
#define FLASHER               0x60

//Infinite Animations
#define FLASHINF              0x71
#define FLASHALT              0x72
#define SPARKLE               0x73
#define SPARKLE_FADE          0x74
#define FLAME                 0x75
#define GLOW                  0x76

//Utilities
#define RESTORE_STATE         0xFD
#define SET_ALL               0xFE
#define CLEAR_ALL             0xFF


//FIRE 2012 Defines
#define SPARKING 120
#define COOLING  55

// Parameter 1 = number of pixels in strip
// Parameter 2 = Arduino pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, PIN, NEO_GRB + NEO_KHZ800);

// Global Variables
int x = 0;
byte mode = 0;
byte led = 0;
byte r = 0;
byte g = 0;
byte b = 0;
byte del = 0;
byte rep = 0;

uint32_t blank = strip.Color(0, 0, 0);
uint32_t currColor = strip.Color(0, 0, 0);

// Backup storage for LEDs to restore former state before short animations play
byte ledMatrix[NUM_LEDS][5];
uint32_t ledTime[NUM_LEDS];

void setup() {
  // LED Strip Init
  strip.begin();
  strip.setBrightness(64); // 25% brightness for now
  strip.show(); // Initialize all pixels to 'off'

  // I2C Init Code
  Wire.begin(I2C_ADDRESS);                // join i2c bus with address #8

  cbi(PORTC, 4);
  cbi(PORTC, 5);
  
  Wire.onReceive(receiveEvent); // register event

  randomSeed(analogRead(0));

  Serial.begin(9600);

  //Initialize with blank LED string
  for(int i = 0; i < NUM_LEDS; i++){
   for(int j = 0; j < 5; j++){
    ledMatrix[i][j] = 0;
   }
  }
}

void loop() {

  currColor = strip.Color(r, g, b);

  switch(mode) {
    case RESTORE_STATE:         restoreState();                             break;
    case COLOR_WIPE:            colorWipe();                                break;
    case RAINBOW:               rainbow();                                  break;
    case RAINBOW_CYCLE:         rainbowCycle();                             break;
    case THEATER_CHASE:         theaterChase();                             break;
    case THEATER_CHASE_RAINBOW: theaterChaseRainbow();                      break;
    case FLASHER:               flasher();                                  break;
    case FLASHINF:              flashinf();                                 break;
    case FLASHALT:              flashalt();                                 break;
    case SPARKLE:               sparkle();                                  break;
    case SPARKLE_FADE:          sparkleFade();                              break;
    case FLAME:                 flame();                                    break;
    case GLOW:                  glow();                                     break;

    case SET_ALL:
      for(uint16_t i=0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, currColor);
      }
      break;

    case CLEAR_ALL:
      for(uint16_t i=0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, blank);
      }
      break;

    default:
      refresh();
      break;
  }
  
  strip.show();
}

// Read 7 bytes as command over i2c
void receiveEvent(int bytes) {
  while(Wire.available()) {
    mode = Wire.read();
    led = Wire.read();
    r = Wire.read();
    g = Wire.read();
    b = Wire.read();
    del = Wire.read();
    rep = Wire.read();
  }
  if(mode == SET_SINGLE_COLOR) {
      ledMatrix[led][0] = r;
      ledMatrix[led][1] = g;
      ledMatrix[led][2] = b;
      ledMatrix[led][3] = del;
      ledMatrix[led][4] = rep;
      mode = 0x00;
  }
}

void refresh() {
  for(int i = 0; i < NUM_LEDS; i++){
    if(ledMatrix[i][4] == 1) {
      uint32_t diff = millis() - ledTime[i];
      if(diff <= ledMatrix[i][3]) {
        strip.setPixelColor(i, strip.Color(ledMatrix[i][0], ledMatrix[i][1], ledMatrix[i][2]));
      }
      else if(diff > ledMatrix[i][3] && diff < ledMatrix[i][3]*2) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
      }
      else {
        ledTime[i] = millis();
      }
    }
    else {
      strip.setPixelColor(i, strip.Color(ledMatrix[i][0], ledMatrix[i][1], ledMatrix[i][2]));
    }
  }
  strip.show(); 
}

// Restore back to individually set configuration
void restoreState() {
  mode = 0x00;
}

void flasher() {
  for(uint16_t j=0; j < rep; j++){
    for(uint16_t i=0; i < NUM_LEDS; i++) {
      if(mode != FLASHER) { return; }
      strip.setPixelColor(i, strip.Color(r, g, b));
      strip.show();
    }
    delay(del);
    for(uint16_t k=0; k < NUM_LEDS; k++) {
      if(mode != FLASHER) { return; }
      strip.setPixelColor(k, blank);
      strip.show();
    }
    delay(del);
  }
  mode = 0x00;  // Run once only
  restoreState();
}

void flashinf() {
  while(mode == FLASHINF) {
    for(uint16_t i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, strip.Color(r, g, b));
      strip.show();
    }
    delay(del);
    for(uint16_t k = 0; k < NUM_LEDS; k++) {
      strip.setPixelColor(k, blank);
      strip.show();
    }
    delay(del);
  }
}

void flashalt() {
  byte start = 0;
  while(mode == FLASHALT) {
    start = start ^ 1;
    for(uint16_t i = start; i < NUM_LEDS; i += 2) {
      strip.setPixelColor(i, strip.Color(r, g, b));
      strip.show();
    }
    delay(del);
    for(uint16_t k = 0; k < NUM_LEDS; k++) {
      strip.setPixelColor(k, blank);
      strip.show();
    }
    delay(del);
  }
}

void sparkle() {
  while(mode == SPARKLE) {
    for(uint16_t i = 0; i <  NUM_LEDS; i++) {
      byte col = (random(10)==0);
      strip.setPixelColor(i, strip.Color(col*r, col*g, col*b));
      strip.show();
    }
    delay(del);
  }
}

void sparkleFade() {
  static byte leds[NUM_LEDS][3];
  memset(leds,0,sizeof(leds));
  
  while(mode == SPARKLE_FADE) {
    for(uint16_t i = 0; i <  NUM_LEDS; i++) {
      if(random(rep*10) == 0) {
        leds[i][0] = r; 
        leds[i][1] = g;
        leds[i][2] = b;
      }
     leds[i][0] = constrain(leds[i][0] - 3, 0, 255);
     leds[i][1] = constrain(leds[i][1] - 3, 0, 255);
     leds[i][2] = constrain(leds[i][2] - 3, 0, 255);
     strip.setPixelColor(i, strip.Color(leds[i][0], leds[i][1], leds[i][2]));
     strip.show();
    }
    delay(del);
  }
}

// Fill the dots one after the other with a color
void colorWipe() {
  for(uint16_t i=0; i< NUM_LEDS; i++) {
    if(mode != COLOR_WIPE) {
      return; 
    }
    strip.setPixelColor(i, strip.Color(r, g, b));
    strip.show();
    delay(del);
  }
  mode = 0x00; // Run once only
}

void clearall() {
  for(uint16_t i=0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, blank);
  }
  for(int i = 0; i < NUM_LEDS; i++){
   for(int j = 0; j < 3; j++){
    ledMatrix[i][j] = 0;
   }
  }
}

// Rainbow animation, better seen on longer strips
void rainbow() {
  uint16_t i, j;
  while(mode == RAINBOW) {
    for(j=0; j < 256; j++) {
      for(i=0; i < NUM_LEDS; i++) {
        if(mode != RAINBOW) {
          return;
        }
        strip.setPixelColor(i, Wheel((i+j) & 255));
      }
      strip.show();
      delay(del);
    }
  }
}

// Slightly different, this makes the rainbow equally distributed throughout
void rainbowCycle() {
  uint16_t i, j;
  while(mode == RAINBOW_CYCLE) {
    for(j=0; j<256*5; j++) { // 5 cycles of all colors on wheel
      for(i=0; i<  NUM_LEDS; i++) {
        strip.setPixelColor(i, Wheel(((i * 256 /  NUM_LEDS) + j) & 255));
      }
      strip.show();
      delay(del);
      if(mode != RAINBOW_CYCLE) {
        return;
      }
    }
  }
}

//Theatre-style crawling lights.
void theaterChase() {
  while(mode == THEATER_CHASE) {
    for (int q=0; q < 3; q++) {
      for (uint16_t i=0; i <  NUM_LEDS; i=i+3) {
        if(mode != THEATER_CHASE) {
          return;
        }
        strip.setPixelColor(i+q, currColor);    //turn every third pixel on
      }
      strip.show();

      delay(del);

      for (uint16_t i=0; i <  NUM_LEDS; i=i+3) {
        if(mode != THEATER_CHASE) {
          return;
        }
        strip.setPixelColor(i+q, 0);        //turn every third pixel off
      }
    }
  }
}

//Theatre-style crawling lights with rainbow effect
void theaterChaseRainbow() {
  while(mode == THEATER_CHASE_RAINBOW) {
    for (int j=0; j < 256; j++) {     // cycle all 256 colors in the wheel
      for (int q=0; q < 3; q++) {
        for (uint16_t i=0; i <  NUM_LEDS; i=i+3) {
          if(mode != THEATER_CHASE_RAINBOW) {
            return;
          }
          strip.setPixelColor(i+q, Wheel( (i+j) % 255));    //turn every third pixel on
        }
        strip.show();
  
        delay(del);
  
        for (uint16_t i=0; i <  NUM_LEDS; i=i+3) {
          if(mode != THEATER_CHASE_RAINBOW) {
            return;
          }
          strip.setPixelColor(i+q, 0);        //turn every third pixel off
        }
      }
    }
  }
}

void glow() {
  byte col = 0;
  float roll = 0;
  float calc = 0;
  while(mode == GLOW) {
    roll++;
    if(roll > TWO_PI * 100) { roll = 0; }
    for (uint16_t i=0; i <  NUM_LEDS; i++) {
      calc = (-cos(roll/100)+1)*255/2;
      col = (byte)calc;
      strip.setPixelColor(i, strip.Color(col, col, col));
      strip.show();
    }
    delay(del);
  }
}

// Fire2012 library test
void flame() {
  static byte heat[NUM_LEDS];
  byte rnd;
  
  while(mode == FLAME) {
    // Step 1.  Cool down every cell a little
    for( int i = 0; i < NUM_LEDS; i++) {
      rnd = random(0, ((COOLING * 10) / NUM_LEDS) + 2);
      if(heat[i] > rnd) { heat[i] = heat[i] - rnd; }
      else { heat[i] = 0; }
    }
 
    // Step 2.  Heat from each cell drifts 'up' and diffuses a little
    for( int k= NUM_LEDS - 3; k > 0; k--) {
      heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2] ) / 3;
    }
   
    // Step 3.  Randomly ignite new 'sparks' of heat near the bottom
    if( random(0, 255) < SPARKING ) {
      int y = random(7);
      rnd = random(160,255);
      if(heat[y] + rnd < 255) { heat[y] = heat[y] + rnd; }
      else { heat[y] = 255; }
    }
 
    // Step 4.  Map from heat cells to LED colors
    for( int j = 0; j < NUM_LEDS; j++) {
        strip.setPixelColor(j, heatColor(heat[j]));
        strip.show();
    }
    delay(del);
  }
}

uint32_t heatColor(uint8_t temperature) {

  byte hr;
  byte hg;
  byte hb;
  
  // Scale 'heat' down from 0-255 to 0-191,
  // which can then be easily divided into three
  // equal 'thirds' of 64 units each.
  uint8_t t192 = map(temperature, 0, 255, 0, 192);
   
  // calculate a value that ramps up from
  // zero to 255 in each 'third' of the scale.
  uint8_t heatramp = t192 & 0x3F; // 0..63
  heatramp <<= 2; // scale up to 0..252
 
  // now figure out which third of the spectrum we're in:
  if( t192 & 0x80) {
    // we're in the hottest third
    hr = 255; // full red
    hg = 255; // full green
    hb = heatramp; // ramp up blue
   
  } else if( t192 & 0x40 ) {
    // we're in the middle third
    hr = 255; // full red
    hg = heatramp; // ramp up green
    hb = 0; // no blue
   
  } else {
    // we're in the coolest third
    hr = heatramp; // ramp up red
    hg = 0; // no green
    hb = 0; // no blue
  }
 
  return strip.Color(hr, hg, hb);
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}
