BALDEAGLESDK_100G_EXE="/usr/local/bin/BaldEagleSdk_v2_12_00_20190715_cameo_gearbox.py"
BALDEAGLESDK_400G_EXE="/usr/local/bin/BaldEagleSdk_v2_14_18.py"

EXE2=$BALDEAGLESDK_100G_EXE
EXE4=$BALDEAGLESDK_100G_EXE
EXE6=$BALDEAGLESDK_100G_EXE
EXE8=$BALDEAGLESDK_100G_EXE

# credo_auto2468.sh x x x x
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
    EXE2=$BALDEAGLESDK_400G_EXE
fi
if [ $2 -eq 2 ]; then
    EXE4=$BALDEAGLESDK_400G_EXE
fi
if [ $3 -eq 2 ]; then
    EXE6=$BALDEAGLESDK_400G_EXE
fi
if [ $4 -eq 2 ]; then
    EXE8=$BALDEAGLESDK_400G_EXE
fi

d1=$(date +"%s")
#long action here
if [ $1 -ne 0 ]; then
    python $EXE2 2 &
fi
if [ $2 -ne 0 ]; then
    python $EXE4 4 &
fi
if [ $3 -ne 0 ]; then
    python $EXE6 6 &
fi
if [ $4 -ne 0 ]; then
    python $EXE8 8 &
fi
wait

echo "All Process Done"
d2=$(date +"%s")
echo $((d2-d1))"sec"

