#!/bin/bash

echo "$@"

items=
for i in "$@"
do
    items="$items \"$i\""
done

#set -x
set -- $items
#set +x
echo "===="
#set -x
eval set -- $items
#set +x
