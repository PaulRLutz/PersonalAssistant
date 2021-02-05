#!/bin/bash

android_path=/home/paul/Workspaces/Multi/Assistant/Android/Assistant/models/src/main/assets/sync/a.lm


function banner {
  echo -e "\n\n"
  echo -e $1
  echo -e "\n\n"
}  

banner "clearing old files"
#rm a.binlm a.vocab a.wfreq a.idngram a.lm
banner "generating a.txt"
python links_to_sentences.py > a.txt
banner "text2wfreq"
cat a.txt | text2wfreq > a.wfreq
banner "wfreq2vocab"
cat a.wfreq | wfreq2vocab -top 200 > a.vocab
banner "text2idngram"
cat a.txt | sudo -E $(which text2idngram) -vocab a.vocab > a.idngram
banner "idngram2lm"
idngram2lm -idngram a.idngram -vocab a.vocab -binary a.binlm
idngram2lm -idngram a.idngram -vocab a.vocab -arpa a.lm

banner "replacing a.lm file in android sync folder"
rm android_path
