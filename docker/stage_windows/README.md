# Stage Simulation with RViz for Windows

This Docker configuration allows you to run the Unico Stage simulation with RViz visualization on Windows.

## Prerequisites

1. **Windows 10/11** with Docker Desktop installed
2. **X Server** for Windows (choose one):
   - [VcXsrv](https://sourceforge.net/projects/vcxsrv/)
   - [Xming](https://sourceforge.net/projects/xming/)

## Setup Instructions

### 1. Install and Configure X Server

#### For VcXsrv:
1. Download and install VcXsrv from the link above
2. Launch XLaunch
3. Select "Multiple windows" and set Display number to 0
4. Select "Start no client"
5. Check "Disable access control" (important for allowing Docker containers to connect)
6. Save the configuration for future use

#### For Xming:
1. Download and install Xming from the link above
2. Launch Xming with the `-ac` flag (to disable access control)

### 2. Build the Docker Image

1. Clone the repository and its dependencies:
   ```bash
   # Clone all required repositories
   git clone <repository-url>/unico_bringup.git
   git clone <repository-url>/unico_description.git
   git clone <repository-url>/unico_stage.git
   git clone <repository-url>/unico_environments.git
   ```

2. Navigate to the workspace root directory (where all repositories are cloned)

3. Run the build script:
   ```bash
   ./unico_bringup/docker/stage_windows/build.sh
   ```

### 3. Run the Docker Container

#### Option 1: Using the run script (recommended)

```bash
./unico_bringup/docker/stage_windows/run.sh
```

#### Option 2: Manual run with PowerShell

1. Find your Windows IP address:
   ```
   ipconfig
   ```

2. Set the DISPLAY environment variable and run the container:
   ```powershell
   $env:DISPLAY="YOUR_IP_ADDRESS:0.0"
   docker run -it --rm -e DISPLAY=$env:DISPLAY --network="host" cmeresearch/stage_windows:1.0
   ```

#### Option 3: For WSL2 users

```bash
export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0.0
docker run -it --rm -e DISPLAY=$DISPLAY --network="host" cmeresearch/stage_windows:1.0
```

## Controlling the Robot

The simulation includes a MQTT broker. To move the robot, send a Twist message to the MQTT topic "command":

```json
{
    "linear": {
        "y": 0,
        "x": 1,
        "z": 0
    },
    "angular": {
        "y": 0,
        "x": 0,
        "z": 0
    }
}
```

## Troubleshooting

1. **No display/RViz doesn't appear**:
   - Make sure your X server is running and configured to allow connections
   - Check that your DISPLAY environment variable is set correctly
   - Try using the IP address of your Windows host instead of `host.docker.internal`

2. **Connection refused**:
   - Check your firewall settings and ensure it allows connections to your X server
   - Make sure you've enabled "Disable access control" in your X server configuration

3. **Performance issues**:
   - RViz can be resource-intensive. Consider using a headless configuration if performance is poor