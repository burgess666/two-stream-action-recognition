#!/bin/sh
#sbatch --job-name=KQ_temporal --gres=gpu:0 --mem=650000 --cpus-per-task=4 --output=output/output_temporal_train.out launch_temporal_train.sh

python3 temporal_train.py
