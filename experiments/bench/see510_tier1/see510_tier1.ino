// SEE 510 Tier 1 bench: bright-light polarization BB84 analogue (systems/see510/10_real_world_experiments.md).
// Arduino Uno or Nano. Host protocol (115200 baud, one line each way), driven by `python -m qll.link.bench_tier1`:
//   P <alice_deg> <bob_deg>      Site A's laser through Site A's polarizer and Site B's analyzer -> "V <adc>"
//   E <alice_deg> <eve_deg>      Site A's laser into the intercept station's analyzer             -> "V <adc>"
//   R <eve_out_deg> <bob_deg>    the station's laser and polarizer into Site B's analyzer         -> "V <adc>"
// Wiring: servos (SG90 class, 5 V from a separate supply, grounds joined) on pins 9 (Site A polarizer),
// 10 (Site B analyzer), 5 (station analyzer), 6 (station re-send polarizer); laser modules (class 2, <= 1 mW,
// 650 nm) switched by a logic-level MOSFET or the module's enable pin on 7 (Site A) and 8 (station); photodiodes
// (BPW34 class into a 100 k to 1 M load resistor, or a TIA) on A0 (Site B) and A1 (station).
// Never look into a laser or along the beam; keep the beam path below eye level and terminate it on the photodiode.
#include <Servo.h>

const int PIN_SERVO_A = 9, PIN_SERVO_B = 10, PIN_SERVO_EIN = 5, PIN_SERVO_EOUT = 6;
const int PIN_LASER_A = 7, PIN_LASER_E = 8;
const int PIN_PD_B = A0, PIN_PD_E = A1;
const int SETTLE_MS = 300;      // servo travel and vibration damping; raise it if readings scatter
const int LASER_MS = 20;        // laser on before reading (photodiode and load settle)
const int SAMPLES = 16;         // readings averaged per pulse

Servo servoA, servoB, servoEin, servoEout;
int lastA = -1, lastB = -1, lastEin = -1, lastEout = -1;

void setAngle(Servo &s, int &last, int deg) {
  if (deg != last) { s.write(deg); last = deg; delay(SETTLE_MS); }
}

int readPd(int pin) {
  long sum = 0;
  for (int i = 0; i < SAMPLES; i++) { sum += analogRead(pin); delayMicroseconds(200); }
  return (int)(sum / SAMPLES);
}

int fire(int laserPin, int pdPin) {
  digitalWrite(laserPin, HIGH);
  delay(LASER_MS);
  int v = readPd(pdPin);
  digitalWrite(laserPin, LOW);
  return v;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LASER_A, OUTPUT); pinMode(PIN_LASER_E, OUTPUT);
  digitalWrite(PIN_LASER_A, LOW); digitalWrite(PIN_LASER_E, LOW);
  servoA.attach(PIN_SERVO_A); servoB.attach(PIN_SERVO_B);
  servoEin.attach(PIN_SERVO_EIN); servoEout.attach(PIN_SERVO_EOUT);
  Serial.println("SEE510 tier1 ready");
}

void loop() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() < 3) return;
  char cmd = line.charAt(0);
  int sp = line.indexOf(' ', 2);
  int a = line.substring(2, sp).toInt();
  int b = line.substring(sp + 1).toInt();
  int v = -1;
  if (cmd == 'P') { setAngle(servoA, lastA, a); setAngle(servoB, lastB, b); v = fire(PIN_LASER_A, PIN_PD_B); }
  else if (cmd == 'E') { setAngle(servoA, lastA, a); setAngle(servoEin, lastEin, b); v = fire(PIN_LASER_A, PIN_PD_E); }
  else if (cmd == 'R') { setAngle(servoEout, lastEout, a); setAngle(servoB, lastB, b); v = fire(PIN_LASER_E, PIN_PD_B); }
  Serial.print("V "); Serial.println(v);
}
