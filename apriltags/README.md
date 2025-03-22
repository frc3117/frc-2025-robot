# Setup
```
wget https://cdn.mickjosh.com/frc/2025/apriltags-setup.sh
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

# Reboot Service
```
sudo systemctl restart frc_apriltags.service
```

# Service Status
```
sudo systemctl status frc_apriltags.service
```

# Service Log
```
journalctl -u frc_apriltags.service
```