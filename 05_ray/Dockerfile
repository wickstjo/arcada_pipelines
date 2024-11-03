# Dockerfile for Ray
FROM rayproject/ray:latest

# Optional: Install additional dependencies
RUN pip install torch tensorflow  # Or any other dependencies you need

# Set environment variables for Ray
ENV RAY_MEMORY_MONITOR_ERROR_THRESHOLD=1.0

# Expose the default ports
EXPOSE 6379 8265