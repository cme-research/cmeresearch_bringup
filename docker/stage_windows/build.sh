#!/bin/bash

# This script builds the Docker image for Stage simulation with RViz for Windows

echo "Building Docker image for Stage simulation with RViz for Windows"
echo "This should be run from the root of your workspace to ensure all packages are found"
echo ""

# Check if we're in the right directory
if [ ! -d "cmeresearch_bringup" ] || [ ! -d "unico_description" ]; then
  echo "Error: This script should be run from the root of your workspace"
  echo "Please cd to the workspace root directory and run:"
  echo "  ./cmeresearch_bringup/docker/stage_windows/build.sh"
  exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build . -f cmeresearch_bringup/docker/stage_windows/Dockerfile --tag cmeresearch/stage_windows:1.0

echo ""
echo "Build complete. To run the container on Windows:"
echo "1. Install an X server (VcXsrv or Xming)"
echo "2. Configure it to allow connections from any host"
echo "3. Run the container with:"
echo "   ./cmeresearch_bringup/docker/stage_windows/run.sh"