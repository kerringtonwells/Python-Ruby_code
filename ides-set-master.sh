#!/bin/bash
set -x
master="iadd1pli05rp001.ihgint.global"
day=$(date +%d)
releasedate=$(date +%Y%m15)
baserepo=$(pulp-admin rpm repo list |
grep Id |
grep -vE "[[:digit:]]{8}$" |
grep -E 'redhat|centos|epel'|
awk '{print $2}')

if [ $day == 18 ]
then
  for i in $baserepo
  do
   #pulp-admin rpm repo create --repo-id $i-$releasedate --relative-url $i-$releasedate --serve-http true
    pulp-admin rpm repo create --repo-id $i-$releasedate --relative-url $i-$releasedate --serve-http true --feed http://$master/pulp/repos/$i-$releasedate/
    pulp-admin rpm repo update --repo-id $i-$releasedate
    pulp-admin rpm repo sync run --repo-id $i-$releasedate
    #pulp-admin rpm repo copy all --from-repo-id $i --to-repo-id $i-$releasedate
    pulp-admin rpm repo publish run --repo-id $i-$releasedate
    logger "$0 --- Created $i-$releasedate"
  done
else
  logger "$0 --- Not the Ides!"
fi
set +x


