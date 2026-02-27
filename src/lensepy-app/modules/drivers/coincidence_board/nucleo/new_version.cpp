 /*  
 *  Structure of a main file for embedded project @ Solec/LEnsE
 *		This code will count the number of pulse there is on each input of the Nucleo card (there is a counter for each input). 
 *		The goal is to have the number of pulse on each input during a time T_int. When this time is over, the counters resets to 0.
 * 		With that, we give the datas of the counters to Python which will calculate 
 * 		the g2 fonction (which depends on every pulse on every input).
 *****************************************************************
 *  Pinout :
 *      - signal_A /    Input for a numerical signal on PA1 port of the Nucleo
 *      - signal_AB /   Input for a numerical signal on PA8 port of the Nucleo
 *      - signal_AC /   Input for a numerical signal on PB5 port of the Nucleo
 *      - signal_ABC /  Input for  numerical signal on PA9 port of the Nucleo
 *      - signal_B /  Input for  numerical signal on PA4 port of the Nucleo
 *      - signal_C /  Input for  numerical signal on PA6 port of the Nucleo
 *      - T_int /       It is the time a user choose to do the measurement of g2
 *****************************************************************
 *  Tested with Nucleo G431KB board / Mbed OS 6
 *****************************************************************
 *  Authors : J.DUBOEUF and N.LE LAY / LEnsE - Creation 2025/02/05
 *		Main modification by J. VILLEMEJANE - 2026/02/25
 *****************************************************************
 *  ProTIS / https://lense.institutoptique.fr/
 *      Based on Mbed OS 6 example : mbed-os-example-blinky-baremetal
 */
 
/*
 *	New protocol / Transfer baudrate = 115200
 *		!T:val? --> !T;		Send Sampling Period to sample data - integer in ms
 *		!D?			--> !D:v_a:v_b:v_c:v_ab:v_ac:v_abc;
 *											Send data
 *		!V?			--> !V:val;		Version of the Hardware
 *		others 	-->	!E;		Error detected in transmission
 */
 


#include "mbed.h"
const char version[] = "1.1a";

//// Input and outputs
UnbufferedSerial      usb_pc(USBTX, USBRX);

InterruptIn signal_A(PA_1);        // It defines a numerical signal to the PA1 port of the Nucleo.
InterruptIn signal_AB(PA_8);        // It defines a numerical signal to the PA8 port of the Nucleo.
InterruptIn signal_AC(PB_5);        // It defines a numerical signal to the PB5 port of the Nucleo.
InterruptIn signal_ABC(PA_9);        // It defines a numerical signal to the PA9 port of the Nucleo.
InterruptIn signal_B(PA_4);        // It defines a numerical signal to the PA4 port of the Nucleo.
InterruptIn signal_C(PA_6);        // It defines a numerical signal to the PA6 port of the Nucleo.

//// Functions prototypes
void ISR_my_pc_reception(void);
void ISR_reset_counters();
void blind_all();
void unblind_all();

//// Global variables
// Serial communication
char input_string[20] = "";      // a String to hold incoming data
char output_string[20] = "";     // a String to hold outcoming data
bool string_complete = false;  // whether the string is complete
int input_cnt = 0;
bool is_ok = false;

// Data acquisition
int T_int = 10;		// Sampling period in ms

int     counter_A = 0;        // It sets counter to 0, counter_A is the number of time a pulse appears on A output
int     counter_AB = 0;       // It sets counter to 0, counter_AB is the number of time a pulse appears on AB output
int     counter_AC = 0;       // It sets counter to 0, counter_AC is the number of time a pulse appears on AC output
int     counter_ABC = 0;      // It sets counter to 0, counter_ABC is the number of time a pulse appears on ABC output
int     counter_B = 0;      // It sets counter to 0, counter_B is the number of time a pulse appears on ABC output
int     counter_C = 0;      // It sets counter to 0, counter_C is the number of time a pulse appears on ABC output

int cnt_A_bckp = 0, cnt_B_bckp = 0, cnt_C_bckp = 0, cnt_AB_bckp = 0, cnt_AC_bckp = 0, cnt_ABC_bckp = 0;

Ticker reset_ticker;             // Ticker which resets the counters


//// Main function
int main()
{    
    usb_pc.baud(115200);
    usb_pc.attach(&ISR_my_pc_reception, UnbufferedSerial::RxIrq);

		sprintf(output_string, "HOM Test / LEnsE");
		usb_pc.write(output_string, strlen(output_string));

	while (true){
		// print the string when a newline arrives:
		if (string_complete) {
				// Action to do
			switch(input_string[1]){
				case 'D':	// Get data
					unblind_all();
					is_ok = false;
					reset_ticker.attach(&ISR_reset_counters, std::chrono::milliseconds(T_int));
					while(is_ok == false){
						thread_sleep_for(1);
					}
					sprintf(output_string, "!D:%d:%d:%d:%d:%d:%d;", cnt_A_bckp, cnt_B_bckp, cnt_C_bckp, cnt_AB_bckp, cnt_AC_bckp, cnt_ABC_bckp);
					usb_pc.write(output_string, strlen(output_string));
					break;
				case 'T':	// Set timing
					sscanf(input_string, "!T:%d?", &T_int);
					sprintf(output_string, "!T:%d;", T_int);
					usb_pc.write(output_string, strlen(output_string));
					break;
				case 'V':	// Version
					sprintf(output_string, "!V:%s;", version);
					usb_pc.write(output_string, strlen(output_string));
					break;
				case 'S':	// Stop
					reset_ticker.detach();
					blind_all();
				default:	// Error
					sprintf(output_string, "!E;");
					usb_pc.write(output_string, strlen(output_string));
			}	

			input_cnt = 0;
			sprintf(output_string, "");
			string_complete = false;
		}
		thread_sleep_for(10);
	}
}

// Interrupt Sub Routine for Serial incoming data
void ISR_my_pc_reception(void){
    char in_char;
    usb_pc.read(&in_char, 1);     // get the received byte   
    if(in_char == '!'){
        input_cnt = 0;
    }
    else{
        input_cnt += 1;
    }
    // add it to the inputString:
    input_string[input_cnt] = in_char;
    // end of command !
    if (in_char == '?') {
      string_complete = true;
    }
}

// Sampling function
void ISR_reset_counters() {
  // Stop actual ticker
  reset_ticker.detach();
	// Collect data
	blind_all();
	cnt_A_bckp = counter_A;
	cnt_B_bckp = counter_B;
	cnt_C_bckp = counter_C;
	cnt_AB_bckp = counter_AB;
	cnt_AC_bckp = counter_AC;
	cnt_ABC_bckp = counter_ABC;
	unblind_all();
	is_ok = true;
	// Reset all the counters
  counter_A = 0;
  counter_AB = 0;
  counter_AC = 0;
  counter_ABC = 0;
  counter_B = 0;
  counter_C = 0;
}


void rising_A() {
	counter_A++;  // add +1 to counter_A
}
void rising_B() {
	counter_B++;  // add +1 to counter_B
}
void rising_C() {
	counter_C++;  // add +1 to counter_C
}
void rising_AB() {
	counter_AB++;  // add +1 to counter_AB
}
void rising_AC() {
	counter_AC++;  // add +1 to counter_AC
}
void rising_ABC() {
	counter_ABC++;  // add +1 to counter_ABC
}

void blind_all(){
	signal_A.rise(NULL);
	signal_B.rise(NULL);
	signal_C.rise(NULL);
	signal_AB.rise(NULL);
	signal_AC.rise(NULL);
	signal_ABC.rise(NULL);
}

void unblind_all(){
	signal_A.rise(&rising_A);
	signal_B.rise(&rising_B);
	signal_C.rise(&rising_C);
	signal_AB.rise(&rising_AB);
	signal_AC.rise(&rising_AC);
	signal_ABC.rise(&rising_ABC);
}