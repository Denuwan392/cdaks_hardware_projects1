#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "HX711.h"
#include <EEPROM.h>
const int HX711_DT = 10;
const int HX711_SCK = 11;
HX711 scale;
LiquidCrystal_I2C lcd(0x27, 20, 4);  
void setup() {
  Serial.begin(57600);
  scale.begin(HX711_DT, HX711_SCK);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Starting Calibration");
  Serial.println("Calibration Started");
  lcd.setCursor(0, 1);
  lcd.print("Remove all weight...");
  Serial.println("Remove all weight...");
  delay(5000);
  scale.tare();
  lcd.setCursor(0, 2);
  lcd.print("Now add known wt...");
  Serial.println("Add known weight...");
  delay(5000);
  long rawReading = scale.get_units(10);
  lcd.setCursor(0, 3);
  lcd.print("Raw: ");
  lcd.print(rawReading);
  Serial.print("Raw reading: ");
  Serial.println(rawReading);
  Serial.println("Enter known weight in grams:");
  while (Serial.available() == 0);  
  float knownWeight = Serial.parseFloat();
  if (knownWeight <= 0) {
    Serial.println("Invalid input. Restart.");
    lcd.clear();
    lcd.setCursor(0, 1);
    lcd.print("Invalid Weight!");
    while (1);
  }
  float calibration_factor = rawReading / knownWeight;
  scale.set_scale(calibration_factor);
  EEPROM.put(0, calibration_factor);
  Serial.print("Calibration factor saved: ");
  Serial.println(calibration_factor, 6);
  lcd.clear();
  lcd.setCursor(0, 1);
  lcd.print("Calib Saved:");
  lcd.setCursor(0, 2);
  lcd.print(calibration_factor, 6);
}
void loop() {
}