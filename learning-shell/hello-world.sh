#!/bin/bash

echo "$0"
echo "$@"

arg = ${5:-0}
echo $arg

if [ -e /opt/eayun/eayuncenter ];then
    echo "Eayuncenter已经安装，是否覆盖以前版本?(y/n)";
    read yes_no

    if [ $yes_no = 'y' -o $yes_no = 'Y' ];then
        echo "覆盖";
    else
        echo "正在取消安装...";
        #sleep 3;
        echo "取消安装成功!";
        exit 99;
    fi;
fi;
