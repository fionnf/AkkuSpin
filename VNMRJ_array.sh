
for i in $(seq 1 10000);
do
    send2Vnmr ~/vnmrsys/.talk "FLUORINE nt=32 setsw(0,-190) gain=30 cpgo"
    sleep 90
    send2Vnmr ~/vnmrsys/.talk "svf('19F_'+time_run)"
    sleep 60
    send2Vnmr ~/vnmrsys/.talk "FLUORINE wet1D nt=32 setsw(0,-190) wetpeaks=1 gain=30 cpgo"
    sleep 90
    send2Vnmr ~/vnmrsys/.talk "svf('19F_sup_'+time_run)"
    sleep 60
    send2Vnmr ~/vnmrsys/.talk "PROTON text('Proto') nt=16 gain=0 cpgo"
    sleep 90
    send2Vnmr ~/vnmrsys/.talk "svf('1H_'+time_run)"
    sleep 60
done
