#!/bin/bash
singularity exec -B /scratch-persistent /home/software/singularity/base.simg:latest jupyter notebook
