# !/bin/bash

user=yangzhou

rdma0=apt137.apt.emulab.net
rdma1=apt141.apt.emulab.net
rdma2=apt146.apt.emulab.net
rdma3=apt147.apt.emulab.net

# clientHosts=($rdma1 $rdma2 $rdma3)
clientHosts=($rdma1)

for i in ${!clientHosts[@]}; do
    host=${clientHosts[$i]}
    echo $i
    rsync -auv -e "ssh -o StrictHostKeyChecking=no" --exclude-from 'sync_exclude_list.txt' ~/rdma_bench/ $user@$host:~/rdma_bench/
done

cd ~/rdma_bench/herd && ./kill.sh; ./do.sh && ./run-servers.sh &> $rdma0.log

for i in ${!clientHosts[@]}; do
    host=${clientHosts[$i]}
    ssh $user@$host "cd ~/rdma_bench/herd && ./kill.sh && ./do.sh && ./run-machine.sh $i" &> $host.log
done
