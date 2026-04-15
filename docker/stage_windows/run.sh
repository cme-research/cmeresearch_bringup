#!/bin/bash

# This script runs the Stage simulation with RViz for Windows
# It assumes you have Docker installed on Windows and an X server running

# For Windows, you need to:
# 1. Install an X server like VcXsrv or Xming
# 2. Configure it to allow connections from any host
# 3. Find your host IP address (ipconfig in cmd)
# 4. Set the DISPLAY environment variable to your_ip:0.0

# Example usage on Windows (PowerShell):
# $env:DISPLAY="192.168.1.100:0.0"
# docker run -it --rm -e DISPLAY=$env:DISPLAY cmeresearch/stage_windows:1.0

# For Windows WSL2:
echo "Running Stage simulation with RViz for Windows"
echo "Make sure you have an X server running on your Windows host"
echo ""
echo "For Windows with WSL2, you can use:"
echo "export DISPLAY=\$(grep nameserver /etc/resolv.conf | awk '{print \$2}'):0.0"
echo ""
echo "For Windows without WSL2, use your host IP address:"
echo "export DISPLAY=your_windows_ip:0.0"
echo ""

# Run the container with display forwarding
# Note: host.docker.internal resolves to the host IP in Docker Desktop for Windows
docker run -it --rm \
  -e DISPLAY=host.docker.internal:0.0 \
  --network="host" \
  cmeresearch/stage_windows:1.0