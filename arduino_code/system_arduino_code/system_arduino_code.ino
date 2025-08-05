#include <Wire.h>
  #include <LiquidCrystal_I2C.h>
  #include "HX711.h"
  #include <EEPROM.h>

  const int HX711_DT = 10;
  const int HX711_SCK = 11;
  HX711 scale;
  float calibration_factor = 1.0;
  const int calValAddress = 0;

  const int stepPin1 = 2;
  const int dirPin1  = 3;
  const int buttonPin = 13;        
  const int relayButtonPin = 5;    
  const int billPin = 8;
  const int relayPin = 12;

  LiquidCrystal_I2C lcd(0x27, 20, 4);
  float weights[3] = {0, 0, 0};  
  int index = 0;
  bool stable = false;
  const int stepsPerRevolution = 200;
  const int totalSteps = stepsPerRevolution * 25;
  const int forwardDelay = 700;
  const int backwardDelay = 400;
  bool relayState = false;
  bool lastRelayButtonState = HIGH;
  bool weighingActive = true;
  float finalWeight = 0;

  void setup() {
    Serial.begin(57600);

    pinMode(stepPin1, OUTPUT);
    pinMode(dirPin1, OUTPUT);
    pinMode(buttonPin, INPUT_PULLUP);
    pinMode(relayButtonPin, INPUT_PULLUP);
    pinMode(relayPin, OUTPUT);
    digitalWrite(relayPin, LOW);
    pinMode(billPin, INPUT_PULLUP);

    lcd.init();
    lcd.backlight();
    lcd.clear();

    scale.begin(HX711_DT, HX711_SCK);
    EEPROM.get(calValAddress, calibration_factor);
    scale.set_scale(calibration_factor);
    scale.tare();
    Serial.print("Loaded calibration factor: ");
    Serial.println(calibration_factor, 6);
    lcd.setCursor(0, 0);
    lcd.print("System OFF          ");
  }
  void loop() {
    bool currentRelayButtonState = digitalRead(relayButtonPin);
    if (lastRelayButtonState == HIGH && currentRelayButtonState == LOW) {
      relayState = !relayState;
      digitalWrite(relayPin, relayState ? HIGH : LOW);
      if (relayState) {
        Serial.println("System ON");
        lcd.setCursor(0, 0);
        lcd.print("Ready - Place Fruit ");
      } else {
        Serial.println("System OFF");
        Serial.println("reset");
        lcd.setCursor(0, 0);
        lcd.print("System OFF          ");
        lcd.setCursor(0, 2);
        lcd.print("                    "); 
      }
      delay(50);
    }
    lastRelayButtonState = currentRelayButtonState;
    if (digitalRead(billPin) == LOW) {
      delay(50); 
      while (digitalRead(billPin) == LOW) delay(10); // wait for release
      Serial.println("bill"); 
    }

    if (!weighingActive) {
      delay(200);
      return;
    }

    if (!relayState) {
      delay(200);
      return;
    }

    float weight = getSmoothedWeight(15);
    float roundedWeight = round(weight);

    weights[index] = roundedWeight;
    index = (index + 1) % 3;  
    lcd.setCursor(0, 2);
    lcd.print("Weight: ");
    lcd.print(roundedWeight, 0);
    lcd.print(" g      ");
    Serial.println(roundedWeight);

    if (roundedWeight < 1.0) {
      lcd.setCursor(0, 0);
      lcd.print("Place the fruit     ");
      stable = false;
      return;
    }

    bool isStable =
      abs(weights[0] - weights[1]) < 1.0 &&
      abs(weights[1] - weights[2]) < 1.0;
    if (isStable && !stable) {
      stable = true;
      lcd.setCursor(0, 0);
      lcd.print("Press Button to Cont");
      Serial.println("Stable weight. Waiting for button press...");
    }
    if (stable) {
      if (digitalRead(buttonPin) == LOW) {
        delay(50);
        while (digitalRead(buttonPin) == LOW) delay(10);
        finalWeight = roundedWeight;
        weighingActive = false;
        Serial.println("add");               
        Serial.print("Final Weight: ");
        Serial.print(finalWeight);
        Serial.println(" g");
        Serial.println("Product added");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Processing...");
        lcd.setCursor(0, 1);
        lcd.print("Please wait...");
        runMotorSequence();
        for (int i = 0; i < 3; i++) weights[i] = 0;
        stable = false;
        weighingActive = true;
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Place the fruit     ");
      }
    } else {
      lcd.setCursor(0, 0);
      lcd.print("Weighing...         ");
    }
    delay(200);
  }
  void runMotorSequence() {
    digitalWrite(dirPin1, LOW);
    for (int i = 0; i < totalSteps; i++) {
      digitalWrite(stepPin1, HIGH);
      delayMicroseconds(forwardDelay);
      digitalWrite(stepPin1, LOW);
      delayMicroseconds(forwardDelay);
    }
    delay(600);
    digitalWrite(dirPin1, HIGH);
    for (int i = 0; i < totalSteps; i++) {
      digitalWrite(stepPin1, HIGH);
      delayMicroseconds(backwardDelay);
      digitalWrite(stepPin1, LOW);
      delayMicroseconds(backwardDelay);
    }
    Serial.println("Motor sequence complete.");
  }
  float getSmoothedWeight(int samples) {
    float total = 0;
    for (int i = 0; i < samples; i++) {
      total += scale.get_units();
      delay(5); 
    }
    return total / samples;
  }