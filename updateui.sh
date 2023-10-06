#!/bin/bash

for path in qt/*; do
#   echo "$path"
   fn=$(basename "$path")
   fn=${fn%.*}
#   echo "$fn"
   pyuic5  "$path" -o "$fn.py"
   echo pyuic5  "$path" -o "$fn.py"
done
