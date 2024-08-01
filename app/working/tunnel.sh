#!/bin/bash
nohup sudo socat TCP-LISTEN:5432 TCP:postgres.cv0ccggam50e.ap-southeast-2.rds.amazonaws.com:5432 &

