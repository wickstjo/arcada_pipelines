#!/bin/bash

# Name of the tmux session
SESSION_NAME="my_tmux_session"

# Create a new tmux session in the background
tmux new-session -d -s $SESSION_NAME

# Split the window into 5 vertical panes
tmux split-window -v -t $SESSION_NAME:0  # First split (into 2)
tmux split-window -v -t $SESSION_NAME:0.0  # Second split (into 3)
tmux split-window -v -t $SESSION_NAME:0.1  # Third split (into 4)
tmux split-window -v -t $SESSION_NAME:0.2  # Fourth split (into 5)
tmux split-window -v -t $SESSION_NAME:0.3  # Fourth split (into 5)

tmux send-keys -t $SESSION_NAME:0.0 'make pipeline.gradual_ingest'
tmux send-keys -t $SESSION_NAME:0.1 'make pipeline.data_refinery' C-m
tmux send-keys -t $SESSION_NAME:0.2 'make pipeline.model_dispatcher' C-m
tmux send-keys -t $SESSION_NAME:0.3 'make pipeline.decision_synthesis' C-m
tmux send-keys -t $SESSION_NAME:0 'make pipeline.post_processing' C-m

# Make the panes equal size
tmux select-layout -t $SESSION_NAME even-vertical

# Select the first pane (optional)
tmux select-pane -t $SESSION_NAME:0.0

# Attach to the tmux session
tmux attach-session -t $SESSION_NAME