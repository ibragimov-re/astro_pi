scp -rp ./src ./start.sh ./setup.py root@orangepi3-lts:/home/astropi/
scp -rp ./astropi.service root@orangepi3-lts:/etc/systemd/system/

#create directory `astropi` ssh root@orangepi3-lts "mkdir -p /home/astropi";

# to turn on autorun of service, execute this:
# sudo systemctl daemon-reexec
# sudo systemctl daemon-reload
# sudo systemctl enable astropi.service

# check status:
# sudo systemctl status astropi.service