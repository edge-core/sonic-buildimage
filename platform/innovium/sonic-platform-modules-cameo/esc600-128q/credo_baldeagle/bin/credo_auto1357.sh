BALDEAGLESDK_100G_EXE="/usr/local/bin/BaldEagleSdk_v2_12_00_20190715_cameo_gearbox.py"
BALDEAGLESDK_400G_EXE="/usr/local/bin/BaldEagleSdk_v2_14_18.py"

EXE1=$BALDEAGLESDK_100G_EXE
EXE3=$BALDEAGLESDK_100G_EXE
EXE5=$BALDEAGLESDK_100G_EXE
EXE7=$BALDEAGLESDK_100G_EXE

# credo_auto1357.sh x x x x
#   x: type of PHY module, 1 = 100G, 2 = 400G, 0 = don't init
if [ $# -ne 4 ]; then
    echo "invalid parameter"
    exit 1
fi

for var in $1 $2 $3 $4
do
    if [ $var -lt 0 ] || [ $var -gt 2 ]; then
        echo "invalid parameter"
        exit 1
    fi
done

if [ $1 -eq 2 ]; then
    EXE1=$BALDEAGLESDK_400G_EXE
fi
if [ $2 -eq 2 ]; then
    EXE3=$BALDEAGLESDK_400G_EXE
fi
if [ $3 -eq 2 ]; then
    EXE5=$BALDEAGLESDK_400G_EXE
fi
if [ $4 -eq 2 ]; then
    EXE7=$BALDEAGLESDK_400G_EXE
fi

d1=$(date +"%s")
#long action here
if [ $1 -ne 0 ]; then
    python $EXE1 1 &
fi
if [ $2 -ne 0 ]; then
    python $EXE3 3 &
fi
if [ $3 -ne 0 ]; then
    python $EXE5 5 &
fi
if [ $4 -ne 0 ]; then
    python $EXE7 7 &
fi
wait

echo "All Process Done"
d2=$(date +"%s")
echo $((d2-d1))"sec"
