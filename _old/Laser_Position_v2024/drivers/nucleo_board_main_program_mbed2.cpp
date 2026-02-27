/****************************************************************************/
/*  PID Controller for LASER beam Tracking                                  */
/****************************************************************************/
/*  LEnsE / Institut d'Optique Graduate School                              */
/****************************************************************************/
/*  BETA 1.0 version / Stable                                               */
/*  Developped by students in PIMS projects / 2021                          */
/*      - Cyrille DES COGNETS                                               */
/*      - Théo MARTIN                                                       */
/*      - Igor RESHETNIKOV                                                  */
/*  Supervised by Caroline KULCSAR and Julien VILLEMEJANE                   */
/*      Update 2023/09/01 by Julien VILLEMEJANE                             */
/****************************************************************************/
/*  Brochage                                                                */
/*      TO COMPLETE                                                         */
/****************************************************************************/
/*  Tested on a Nucleo-L476RG board                                         */
/*  Matlab App interface required                                           */
/****************************************************************************/

#include "mbed.h"
#include "dsp.h"
#define maxX        0.5
#define PER_ACQ     0.0001
#define PER_STEP    0.0001
#define PER_LED     2000
#define MAX_CHAR    256
#define N_SAMPLES   1024

/* Modules pour Asservissement */
Ticker      tik_asst;
AnalogIn    inX(PC_2);
AnalogIn    inY(PC_0);
AnalogOut   outX(PA_4);
AnalogOut   outY(PA_5);
DigitalOut  out_led(D5);
DigitalOut  debug_out(D4);
arm_pid_instance_f32    pidX;
arm_pid_instance_f32    pidY;
/* Modules pour communication avec Matlab */
//Serial          pc(PC_10, PC_11); //TX - transmission, RX - reception
Serial          pc(USBTX, USBRX); //TX - transmission, RX - reception
InterruptIn     button (USER_BUTTON);

/* Variables globales pour Asservissement */
char    mode = '0';
double g_Kpx = 1;
double g_Kix = 0;
double g_Kdx = 0;
double g_Kpy = 1;
double g_Kiy = 0;
double g_Kdy = 0;
double g_sampling_frequency = 1000;
double g_sampling_period;
int g_samples = 100;
int g_indice = 0;
double g_sine_freq = 1;
/* Variables gloables pour Rampe / Step */
double valX;
int signeX;
double pasX = 0.01;
double samplesX[N_SAMPLES];
double samplesY[N_SAMPLES];
double samplesSTEP[N_SAMPLES];
int g_trig;
/* Variables globales pour communication avec Matlab */
char g_value[MAX_CHAR];
int g_index=0;
char g_ch;
int g_t_temp=0;
char data_ok = 0;
int g_i = 0;
int g_NotFullCommand = 0;
int periode_led = PER_LED;

/* Values for motors position and detector output*/
double g_Ux = 0.5;
double g_Uy = 0.5;
double g_DetX = 0;
double g_DetY = 0;

double g_Ux_toML = 0.0;
double g_Uy_toML = 0.0;
double g_DetX_toML = 0.0;
double g_DetY_toML = 0.0;
/* Values for step response */
double sX_min = 0;
double sX_max = 0;
double sY_min = 0;
double sY_max = 0;
int sIndex = 0;         // index of the data to collect
char sChannel = ' ';    // channel to collect {X, Y, S}
bool sData = false;

/*-------------------------------*/

bool IsAN(char A);
int read_command();
double k_coef(int i);

void updatePID(void);

/* Fonction d'interruption PID - X et Y */
void controlLoop(void)
{
    debug_out = 1;
    //Process the PID controller
    float outxx = arm_pid_f32(&pidX, (float) inX.read() - 0.5f);
    float outyy = arm_pid_f32(&pidY, (float) inY.read() - 0.5f);
    //Range limit the output
    if (outxx < -0.5)
        outxx = -0.5;
    else if (outxx > 0.5)
        outxx = 0.5;
    if (outyy < -0.5)
        outyy = -0.5;
    else if (outyy > 0.5)
        outyy = 0.5;
    //Set the new output duty cycle
    outX.write(outxx+0.5);
    outY.write(outyy+0.5);
    debug_out = 0;
    g_t_temp++;
}
/* Fonction d'interruption de test - Step */
void stepLoop(void){
    debug_out = 1;
    if(g_trig == 1){
        if(g_indice == 0){
            g_Ux=0.5+sX_min/200.0;
            g_Uy=0.5+sY_min/200.0;
            outX.write(g_Ux);
            outY.write(g_Uy);
        }
        if(g_indice == N_SAMPLES+10){
            g_Ux=0.5+sX_max/200.0;
            g_Uy=0.5+sY_max/200.0;
            outX.write(g_Ux);
            outY.write(g_Uy);
        }
        if((g_indice >= N_SAMPLES) and (g_indice < 2 * N_SAMPLES)){
            samplesX[g_indice-N_SAMPLES] = 2*100.0*((float) inX.read() - 0.5f);    //Real part NB removing DC offset
            samplesY[g_indice-N_SAMPLES] = 2*100.0*((float) inY.read() - 0.5f);    //Real part NB removing DC offset
            if(g_indice >= N_SAMPLES + 10)
                samplesSTEP[g_indice-N_SAMPLES] = sX_max;
            else
                samplesSTEP[g_indice-N_SAMPLES] = sX_min;
        }
        if(g_indice == 2*N_SAMPLES){
            g_trig = 0;
        }
        g_indice += 1;
    }
    debug_out = 0;
    g_t_temp++;
}

/* Fonction d'interruption de test - Sine */
void sineLoop(void){
    debug_out = 1;
    if(g_trig == 1){
        // Create sinewave at good frequency - TO DO
        double amp_x = sX_max-sX_min;
        double amp_y = sY_max-sY_min;
        g_Ux = amp_x; // TO DO
        g_Uy = amp_y;
        outX.write(g_Ux);
        outY.write(g_Uy);

        // Collect data on inX and inY - TO CHANGE !!
        if((g_indice >= N_SAMPLES) and (g_indice < 2 * N_SAMPLES)){
            samplesX[g_indice-N_SAMPLES] = 2*100.0*((float) inX.read() - 0.5f);    //Real part NB removing DC offset
            samplesY[g_indice-N_SAMPLES] = 2*100.0*((float) inY.read() - 0.5f);    //Real part NB removing DC offset
            if(g_indice >= N_SAMPLES + 10)
                samplesSTEP[g_indice-N_SAMPLES] = sX_max;
            else
                samplesSTEP[g_indice-N_SAMPLES] = sX_min;
        }
        if(g_indice == 2*N_SAMPLES){
            g_trig = 0;
        }
        g_indice += 1;
    }
    debug_out = 0;
    g_t_temp++;
}

/* Fonction d'interruption de test - Rampe */
void rampLoop(void){
    debug_out = 1;
    valX = valX + signeX * pasX;
    if(valX > maxX){ signeX = -1; }
    if(valX < 0.0){ signeX = 1; }
    outX.write(valX);
    debug_out = 0;
    g_t_temp++;
}

/* Interrupt function for Matlab receiving data */
void IT_Rx_Matlab(){
    tik_asst.detach();
    g_ch = pc.getc();   // read it
    if ((g_index<MAX_CHAR-1) and (data_ok == 0)){
        g_value[g_index]=g_ch;  // put it into the value array and increment the index
        g_index++;
    }
    if(g_ch == '\n'){
        g_value[g_index] = '\0';
        g_index=0;
        data_ok = 1;
    }
    mode == '0';
}

/* Interrupt function for switch button */
void IT_button_pressed(void){
    int k=0;
    do{
        pc.putc(g_value[k]);
        k++;
    } while (g_value[k]!='\0');    // loop until the '\n' character
}

/* alignement */
void alignement(void){
    g_DetX_toML=2*100.0*((float) inX.read() - 0.5f);
    g_DetY_toML=2*100.0*((float) inY.read() - 0.5f);
    wait_ms(10);
    pc.printf("%c_%lf_%lf_!\r\n", mode, g_DetX_toML, g_DetY_toML);
}

/* motor */
void motor(void){
    outX.write(g_Ux);
    outY.write(g_Uy);
    g_Ux_toML=2*100*(g_Ux-0.5);
    g_Uy_toML=2*100*(g_Uy-0.5);
    g_DetX_toML=2*100.0*((float) inX.read() - 0.5f);
    g_DetY_toML=2*100.0*((float) inY.read() - 0.5f);
    pc.printf("%c_%lf_%lf_%lf_%lf_!\r\n", mode, g_Ux_toML, g_Uy_toML, g_DetX_toML, g_DetY_toML);
}

/* Decoding commands */
int read_command()
{
    debug_out = 1;
    int i = 0;
    switch(g_value[0]){
        case 'P':
            mode = 'P';
            sscanf(g_value, "P_%lf_%lf_%lf_!\r\n", &g_Kpx, &g_Kpy, &g_sampling_frequency);
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            g_sampling_period = 1.0 / g_sampling_frequency;
            return 1;
        case 'I':
            mode = 'I';
            sscanf(g_value, "I_%lf_%lf_%lf_%lf_%lf_!\r\n", &g_Kpx, &g_Kpy, &g_Kix, &g_Kiy, &g_sampling_frequency);
            g_Kdx = 0; g_Kdy = 0;
            g_sampling_period = 1.0 / g_sampling_frequency;
            return 1;
        case 'D':
            mode = 'D';
            sscanf(g_value, "D_%lf_%lf_%lf_%lf_%lf_%lf_%lf_!\r\n", &g_Kpx, &g_Kpy, &g_Kix, &g_Kiy, &g_Kdx, &g_Kdy, &g_sampling_frequency);
            g_sampling_period = 1.0 / g_sampling_frequency;
            return 1;
        case 'S':  // Step mode
            mode = 'S';
            out_led = 1;
            g_Kpx = 1;  g_Kpy = 1;
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            sscanf(g_value, "S_%lf_%lf_%lf_%lf_%lf_%d_!\r\n", &sX_min, &sX_max, &sY_min, &sY_max, &g_sampling_frequency, &g_samples);
            if(g_samples > N_SAMPLES){
                g_samples = N_SAMPLES;
                pc.printf("S_NK!\r\n");
            }
            else{
                pc.printf("S_OK!\r\n");
            }
            g_sampling_period = 1.0 / g_sampling_frequency;
            g_trig = 1;
            g_indice = 0;
            return 1;
        case 'N':  // Sine mode
            mode = 'N';
            out_led = 1;
            g_Kpx = 1;  g_Kpy = 1;
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            g_sampling_frequency = 10000;
            g_samples = N_SAMPLES;
            sscanf(g_value, "N_%lf_%lf_%lf_%lf_%d_%lf_!\r\n", &sX_min, &sX_max, &sY_min, &sY_max, &g_samples,
            &g_sine_freq);
            pc.printf("N_OK!\r\n");
            g_sampling_period = 1.0 / g_sampling_frequency;
            g_trig = 1;
            g_indice = 0;
            return 1;
        case 'F':
            sscanf(g_value, "F_!\r\n");
            if(g_trig == 1){
                pc.printf("F_0_!\r\n");
            }
            else{
                pc.printf("F_1_!\r\n");
            }
            return 1;
        case 'T':  // Step data
            mode = 'T';
            out_led = 0;
            sscanf(g_value, "T_%c_%d_!\r\n", &sChannel, &sIndex);
            sData = true;
            return 1;
        case 'R':   // Reset Step mode
            sscanf(g_value, "R_!\r\n");
            g_trig = 2;
            g_indice = 0;
            return 1;
        case 'M':
            mode = 'M';
            g_Kpx = 0;  g_Kpy = 0;
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            sscanf(g_value, "M_%lf_%lf_!\r\n", &g_Ux_toML, &g_Uy_toML);
            g_Ux=0.5+g_Ux_toML/200.0;
            g_Uy=0.5+g_Uy_toML/200.0;
            g_sampling_period = 1.0;
            return 1;
        case 'A':
            mode = 'A';
            g_Kpx = 0;  g_Kpy = 0;
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            g_sampling_period = 1.0;
            return 1;
		case 'C':
			mode = 'C';
            g_Kpx = 0;  g_Kpy = 0;
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            g_sampling_period = 1.0;
			return 1;
        case 'O':
            mode = 'O';
            g_Kpx = 0;  g_Kpy = 0;
            g_Kix = 0;  g_Kiy = 0;
            g_Kdx = 0;  g_Kdy = 0;
            g_sampling_period = 1.0;
        default :
            mode = '0';
            return 0;
    }
    debug_out = 0;
}

/* Fonction principale */
int main()
{
    out_led = 0;
    valX = 0;
    signeX = 1;
    pc.baud(115200);
    pc.attach(&IT_Rx_Matlab);
    strcpy(g_value, "Coucou");
    g_value[6] = '\r';
    g_value[7] = '\n';
    /* Button interrupt */
    button.fall(&IT_button_pressed);
    //Initialize the PID instance structure
    updatePID();
    g_sampling_period = (float) PER_ACQ;
    //Run the PID control loop every 1ms
    tik_asst.attach(&controlLoop, g_sampling_period);

    //pc.printf("im here !!\r\n");

    while (true) {

        if(g_t_temp>=periode_led) // LED blinking
        {
            g_t_temp=0;
            out_led = !out_led;
        }

        if((mode == 'S') and (g_trig == 0)){
            tik_asst.detach();
            out_led = 0;
            g_trig = 2;
        }
        if((mode == 'N') and (g_trig == 0)){
            tik_asst.detach();
            out_led = 0;
            g_trig = 2;
        }
        /*

            // SENDING DATA
            for(int i=0; i < g_samples; i++){
                pc.printf("S_x_%d_%lf_!\r\n", i+1, samplesX[i]);
                wait_ms(10);
                pc.printf("S_y_%d_%lf_!\r\n", i+1, samplesY[i]);
                wait_ms(10);
                pc.printf("S_s_%d_%lf_!\r\n", i+1, samplesSTEP[i]);
                wait_ms(10);
            }
            pc.printf("S_END_!\r\n");
            g_trig = 2;
            g_indice = 0;
        }
        */

        if(data_ok){
            tik_asst.detach();
            data_ok = 0;
            g_index = 0;
            int comm_ok = read_command();//recognizing coefficients
            if(comm_ok){
                if((mode == 'P') or (mode == 'I') or (mode == 'D')){
                    //pc.printf("%c_OK! gX = %lf gY = %lf Fe = %lf\r\n", mode, g_Kpx, g_Kpy, g_sampling_frequency);
                    updatePID();
                    tik_asst.attach(&controlLoop, g_sampling_period);
                }
                if(mode == 'S'){
                    tik_asst.attach(&stepLoop, g_sampling_period);
                }
                if(mode == 'N'){
                    tik_asst.attach(&sineLoop, g_sampling_period);
                }
                if(mode == 'F'){

                }
                if(mode == 'T'){
                    if(sData == true){
                        int index = -1;
                        float value = 0;
                        if(sIndex < g_samples){
                            index = sIndex;
                            switch(sChannel){
                                case 'X':
                                    value = samplesX[index];
                                    break;
                                case 'Y':
                                    value = samplesY[index];
                                    break;
                                case 'S':
                                    value = samplesSTEP[index];
                                    break;
                                default:
                                    value = 0;
                                    break;
                            }
                        }
                        pc.printf("T_%c_%d_%lf_!\r\n", sChannel, index, value);
                        sData = false;
                    }
                }
                if(mode == 'A'){
                    outX.write(0.5);
                    outY.write(0.5);
                    alignement();
                }
                if(mode == 'M'){
                    motor();
                }
				if(mode == 'C'){	// Test connection
					pc.printf("C_!\r\n");
				}
                strcpy(g_value, "");
            }
        }     
    } 
}

/* Mise à jour des coefficients */
void updatePID(void){
    switch(mode){
        case 'P' : g_Kix = 0; g_Kiy = 0; g_Kdx = 0; g_Kdy = 0; break;
        case 'I' : g_Kdx = 0; g_Kdy = 0; break;
        case 'D' : break;
        default : g_Kpx = 1; g_Kpy = 1;
    }
    pidX.Kp = g_Kpx;
    pidX.Ki = g_Kix;
    pidX.Kd = g_Kdx;
    arm_pid_init_f32(&pidX, 1);
    pidY.Kp = g_Kpy;
    pidY.Ki = g_Kiy;
    pidY.Kd = g_Kdy;
    arm_pid_init_f32(&pidY, 1);
}
