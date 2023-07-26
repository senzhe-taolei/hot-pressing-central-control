#!/bin/sh
cd ..
python3 reya/yeya.py > logs/yeya_listen.log \
& python3 reya/chengliao.py > logs/chengliao_listen.log \
& python3 reya/robot.py > logs/robot_listen.log \
& python3 reya/yaji.py > logs/yaji_listen.py