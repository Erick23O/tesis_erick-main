#include <Servo.h>
#include <avr/wdt.h>
#include <AccelStepper.h>
#include <MultiStepper.h>


const int ENABLE_PIN = 8; // D8

const int STEP_PIN_X = 2; // A0
const int DIR_PIN_X = 5;  // A1

const int STEP_PIN_Z = 4; // A6
const int DIR_PIN_Z = 7;  // A7

const int servo_apertura = 3;
const int servo_rotacion = 6;



const int relacion_engrane_motor1 = 38;
const int relacion_engrane_motor2 = 54;  //anterior 27

const int homingM1 = 9;
const int homingM2 = 11;
const int final_carrera_3 = 10;
const int final_carrera_4 = 12;

const int ENA = 13;
const int IN1 = 17;
const int IN2 = 14;

long lastTime = 0;
long initial_homing = 0;

bool activado = true;

AccelStepper MOTOR1(1, STEP_PIN_X, DIR_PIN_X); // 1; STEP ; DIR --  X
AccelStepper MOTOR2(1, STEP_PIN_Z, DIR_PIN_Z); // 1; STEP ; DIR --  Z
Servo servo_rot;
Servo servo_apert;

float pos1_step1 = 0.0;
float pos1_step2 = 0.0;

float pos2_step1 = 0.0;
float pos2_step2 = 0.0;

float pos1_step1_auto = 0.0;
float pos1_step2_auto = 0.0;
float pos2_step1_auto = 0.0;
float pos2_step2_auto = 0.0;

float pos3_step1 = 0.0;
float pos3_step2 = 0.0;

float pos4_step1 = 0.0;
float pos4_step2 = 0.0;

MultiStepper steppers;

///////////////////// COMUNICACION SERIAL ////////////////
String inputString_manual = "";
String inputString_auto = "";
bool stringComplete_manual = false;
bool stringComplete_auto = false;
const char separator = ',';
const int dataLength_manual = 4;
const int dataLength_auto = 8;
int datos_manual[dataLength_manual];
int datos_auto[dataLength_auto];

const int angle_F1 = 50; // original 65 para compensar le damos 75°
const int angle_F2 = 25; // original 50 para compensar le damos 70°

void setup()
{
    wdt_disable();
    Serial.begin(9600);
    pinMode(ENABLE_PIN, OUTPUT);
    digitalWrite(ENABLE_PIN, LOW);
    pinMode(homingM1, INPUT_PULLUP);
    pinMode(homingM2, INPUT_PULLUP);
    pinMode(final_carrera_3, INPUT_PULLUP);
    pinMode(final_carrera_4, INPUT);
    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    delay(600);
    servo_apert.attach(servo_apertura);
    servo_rot.attach(servo_rotacion);    
    
    MOTOR1.setMaxSpeed(1500);
    MOTOR2.setMaxSpeed(1500);
    MOTOR1.setSpeed(1500);
    MOTOR2.setSpeed(1500);
    MOTOR1.setAcceleration(5000);
    MOTOR2.setAcceleration(5000);

    // MOTOR1.setCurrentPosition(-1900);
    // MOTOR2.setCurrentPosition(-1350);

    // Multistepper
    steppers.addStepper(MOTOR1);
    steppers.addStepper(MOTOR2);

    home();
}

void reset()
{
    wdt_enable(WDTO_15MS);
    while (1)
    {
    }
}

void home()
{
    MOTOR1.setMaxSpeed(1500);
    MOTOR1.setAcceleration(5000);
    MOTOR2.setMaxSpeed(1500);
    MOTOR2.setAcceleration(5000);

    servo_apert.write(0);
    servo_rot.write(0);
    digitalWrite(ENA, 1);
    digitalWrite(IN1, 1);
    digitalWrite(IN2, 0);
    delay(4000);
    // home motor 1

    while (digitalRead(homingM1))
    {
        MOTOR1.moveTo(initial_homing);
        MOTOR1.setSpeed(-1500);
        initial_homing--;
        MOTOR1.run();
        delay(1);
    }
    delay(500);
    //initial_homing = 0;
    // home motor 2
    while (digitalRead(homingM2))
    {
        MOTOR2.moveTo(initial_homing);
        MOTOR2.setSpeed(-1500);
        initial_homing--;
        MOTOR2.run();
        delay(1);
    }

    long pos_cero_pieza_m1 = angle_F1 * (7600 / 360) + 300;
    long pos_cero_pieza_m2 = angle_F2 * (10800 / 360) ;
    MOTOR1.setCurrentPosition(0);
    MOTOR2.setCurrentPosition(0);
    MOTOR1.moveTo(pos_cero_pieza_m1);
    MOTOR2.moveTo(pos_cero_pieza_m2);
    MOTOR1.setSpeed(1500);
    MOTOR2.setSpeed(1500);
    while (MOTOR1.currentPosition() < pos_cero_pieza_m1)
    {
        MOTOR1.run();
    }
    delay(500);
    while (MOTOR2.currentPosition() < pos_cero_pieza_m2)
    {
        MOTOR2.run();
    }
    MOTOR1.setCurrentPosition(0);
    MOTOR2.setCurrentPosition(0);
    MOTOR1.setCurrentPosition(-1900);
    MOTOR2.setCurrentPosition(-2700);
}

/////////////// RECEPCION DE DATOS /////////////////////
void serialEvent()
{
    while (Serial.available())
    {
        char inChar = (char)Serial.read();
        inputString_manual += inChar;
        inputString_auto += inChar;
        if (inChar == '\n')
        {
            stringComplete_manual = true;
            inChar = ' ';
        }
        if (inChar == '\t')
        {
            stringComplete_auto = true;
            inChar = ' ';
        }
        if (inChar == '\r')
        {
            //home();
            inChar = ' ';
            delay(500);
            reset();
        }
    }
}

void loop()
{

    ////////// SI RECIBE DATOS DE FORMA MANUAL /////////////
    if (stringComplete_manual)
    {
        MOTOR1.setMaxSpeed(1500);
        MOTOR1.setAcceleration(5000);
        MOTOR2.setMaxSpeed(1500);
        MOTOR2.setAcceleration(5000);
        MOTOR1.setSpeed(1500);
        MOTOR2.setSpeed(1500);
        for (int i = 0; i < dataLength_manual; i++)
        {
            int index = inputString_manual.indexOf(separator);
            datos_manual[i] = inputString_manual.substring(0, index).toFloat();
            inputString_manual = inputString_manual.substring(index + 1);
        }

        pos1_step1 = datos_manual[0];
        pos1_step2 = datos_manual[1];
        pos2_step1 = datos_manual[2];
        pos2_step2 = datos_manual[3];

        long positions1[2];
        
        positions1[0] = pos1_step1;                
        positions1[1] = pos1_step2;

        // se mueve  a la posición 1
        steppers.moveTo(positions1);
        steppers.runSpeedToPosition(); 

        delay(1500);
        // se abre el griper
        servo_apert.write(50);
        // baja el actuador
        delay(1500);
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 1);
        delay(2500);
        // servo_rot.write(0);
        servo_apert.write(22);
        delay(1500);
        // sube el actuador
        digitalWrite(IN1, 1);
        digitalWrite(IN2, 0);
        delay(3000);
        
        
        
        long positions2[2];        
        positions2[0] = pos2_step1;
        positions2[1] = pos2_step2;
        // se mueve a la posición 2
        steppers.moveTo(positions2);
        steppers.runSpeedToPosition();
        

        delay(1500);
        // baja el actuador        
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 1);
        delay(2000);
        //suelta la pinza
        servo_apert.write(50);
        delay(1500);
        //sube el actuador
        digitalWrite(IN1, 1);
        digitalWrite(IN2, 0);
        delay(3500);
        servo_apert.write(0);

        inputString_manual = "";
        stringComplete_manual = false;
    }

    ////////// SI RECIBE DATOS DE FORMA AUTOMATICA /////////////
    if (stringComplete_auto == true && stringComplete_manual == false)
    {
        MOTOR1.setMaxSpeed(1500);
        MOTOR1.setAcceleration(5000);
        MOTOR2.setMaxSpeed(1500);
        MOTOR2.setAcceleration(5000);
        for (int i = 0; i < dataLength_auto; i++)
        {
            int index = inputString_auto.indexOf(separator);
            datos_auto[i] = inputString_auto.substring(0, index).toFloat();
            inputString_auto = inputString_auto.substring(index + 1);
        }

        pos1_step1_auto = datos_auto[0];
        pos1_step2_auto = datos_auto[1];

        pos2_step1_auto = datos_auto[2];
        pos2_step2_auto = datos_auto[3];

        pos3_step1 = datos_auto[4];
        pos3_step2 = datos_auto[5];

        pos4_step1 = datos_auto[6];
        pos4_step2 = datos_auto[7];

        long positions1_auto[2];
        positions1_auto[0] = pos1_step1_auto;
        positions1_auto[1] = pos1_step2_auto;
        // se mueve a la posición 1
        steppers.moveTo(positions1_auto);
        steppers.runSpeedToPosition();

        delay(1000);
        //se abre el griper
        servo_apert.write(50);
        // baja el actuador
        delay(1000);
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 1);
        delay(2500);
        // se cierra el griper para sujetar
        servo_apert.write(22);
        delay(2000);
        // sube el actuador
        digitalWrite(IN1, 1);
        digitalWrite(IN2, 0);
        delay(3000);

        long positions2_auto[2];
        positions2_auto[0] = pos2_step1_auto;
        positions2_auto[1] = pos2_step2_auto;
        // se mueve a la posición 3
        steppers.moveTo(positions2_auto);
        steppers.runSpeedToPosition();

        delay(1000);
        
        // baja el actuador
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 1);
        delay(2500);
        // suelta el griper
        servo_apert.write(50);
        delay(2000);
        // sube el actuador
        digitalWrite(IN1, 1);
        digitalWrite(IN2, 0);
        delay(3500);
        servo_apert.write(0);

        delay(2000);

        long positions3[2];
        positions3[0] = pos3_step1;
        positions3[1] = pos3_step2;
        // se mueve a la posición 3
        steppers.moveTo(positions3);
        steppers.runSpeedToPosition();

        delay(2000);
        // se abre el griper
        servo_apert.write(50);
        // baja el actuador
        delay(1500);
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 1);
        delay(2500);
        // se cierra el griper para sujetar
        servo_apert.write(22);
        delay(1500);
        // sube el actuador
        digitalWrite(IN1, 1);
        digitalWrite(IN2, 0);
        delay(3000);

        long positions4[2];
        positions4[0] = pos4_step1;
        positions4[1] = pos4_step2;
        // se mueve a la posición 4
        steppers.moveTo(positions4);
        steppers.runSpeedToPosition();

        delay(1500);
        // baja el actuador
        digitalWrite(IN1, 0);
        digitalWrite(IN2, 1);
        delay(2500);
        // suelta el griper
        servo_apert.write(50);
        delay(1500);
        // sube el actuador
        digitalWrite(IN1, 1);
        digitalWrite(IN2, 0);
        delay(3500);
        // se cierra el griper
        servo_apert.write(0);

        inputString_auto = "";
        stringComplete_auto = false;
    }
}