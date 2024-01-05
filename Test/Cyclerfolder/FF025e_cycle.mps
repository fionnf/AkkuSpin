EC-LAB SETTING FILE

Number of linked techniques : 1

Filename : C:\Users\echem\Desktop\FIONN\FF025\FF025e_cycle.mps

Device : VSP-300
Electrode connection : standard
Ewe ctrl range : min = -2,50 V, max = 2,50 V
Ewe,I filtering : 50 kHz
Channel : Floating
Electrode material : 
Initial state : 
Electrolyte : 
Comments : 
Cable : unknown
Electrode surface area : 0,001 cm²
Characteristic mass : 0,001 g
Equivalent Weight : 0,000 g/eq.
Density : 0,000 g/cm3
Cycle Definition : Charge/Discharge alternance
Do not turn to OCV between techniques

Technique : 1
Modulo Bat
Ns                  0                   1                   2                   3                   
ctrl_type           Rest                CC                  CC                  Loop                
Apply I/C           I                   I                   I                   I                   
ctrl1_val           0,000               0,500               0,500               1,400               
ctrl1_val_unit                          mA                  mA                                      
ctrl1_val_vs                            <None>              <None>                                  
ctrl2_val           0,000               0,000               0,000               0,000               
ctrl2_val_unit                                                                                      
ctrl2_val_vs                                                                                        
ctrl3_val           0,000               0,000               0,000               0,000               
ctrl3_val_unit                                                                                      
ctrl3_val_vs                                                                                        
N                   0,00                0,00                0,00                0,00                
charge/discharge    Charge              Charge              Discharge           Discharge           
charge/discharge_1  Charge              Charge              Charge              Charge              
Apply I/C_1         I                   I                   I                   I                   
N1                  0,00                0,00                0,00                0,00                
ctrl4_val           0,000               0,000               0,000               0,000               
ctrl4_val_unit                                                                                      
ctrl_seq            0                   0                   0                   1                   
ctrl_repeat         0                   0                   0                   0                   
ctrl_trigger        Falling Edge        Falling Edge        Falling Edge        Falling Edge        
ctrl_TO_t           0,000               0,000               0,000               0,000               
ctrl_TO_t_unit      d                   d                   d                   d                   
ctrl_Nd             6                   6                   6                   6                   
ctrl_Na             2                   2                   2                   2                   
ctrl_corr           0                   0                   0                   0                   
lim_nb              1                   1                   1                   0                   
lim1_type           Time                Ewe                 Ewe                 Ewe                 
lim1_comp           >                   >                   <                   >                   
lim1_Q              Q limit             Q limit             Q limit             Q limit             
lim1_value          10,000              1,000               -1,000              -0,600              
lim1_value_unit     s                   V                   V                   V                   
lim1_action         Next sequence       Next sequence       Next sequence       Next sequence       
lim1_seq            1                   2                   3                   4                   
rec_nb              1                   1                   1                   0                   
rec1_type           Time                Time                Time                Time                
rec1_value          1,000               1,000               1,000               1,000               
rec1_value_unit     s                   s                   s                   s                   
E range min (V)     -2,500              -2,500              -2,500              -2,500              
E range max (V)     2,500               2,500               2,500               2,500               
I Range             10 mA               10 mA               10 mA               10 mA               
I Range min         Unset               Unset               Unset               Unset               
I Range max         Unset               Unset               Unset               Unset               
I Range init        Unset               Unset               Unset               Unset               
auto rest           0                   0                   0                   0                   
Bandwidth           5                   5                   5                   5                   
