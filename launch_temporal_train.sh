#!/bin/sh
#sbatch --job-name=KQ_temporal --gres=gpu:1 --mem=8096 --cpus-per-task=4 --output=output/output_temporal_train.out launch_temporal_train.sh

python3 temporal_train.py
