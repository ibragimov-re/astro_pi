ssh root@orangepi3-lts "mkdir -p /home/astropi";
scp -rp ./src ./main.py root@orangepi3-lts:/home/astropi/