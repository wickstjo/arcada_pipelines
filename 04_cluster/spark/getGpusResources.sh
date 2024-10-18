#!/bin/bash
# This script detects the number of GPUs available on the machine and returns it

nvidia-smi -L | wc -l
