#!/bin/bash

python3 functional/utils/wait_for_postgres.py
python3 functional/utils/wait_for_redis.py

pytest functional