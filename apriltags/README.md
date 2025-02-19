# Setup
```
wget https://gist.githubusercontent.com/mickjosh/6bf91403f2259a513eeadc32b782bd22/raw/b534da0801ea5cba01b158e8d7a7960dbb5f42de/apriltags-setup.sh
chmod +x apriltags-setup.sh
./apriltags-setup.sh
```

# Start Service
```
sudo systemctl start frc_apriltags.service
```

# Stop Service
```
sudo systemctl stop frc_apriltags.service
```

# Service Status
```
sudo systemctl status frc_apriltags.service
```

# Service Log
```
journalctl -u frc_apriltags.service
```