import os
import signal
import sys
import time
import subprocess

user = 'yangzhou'
# the first host is the localhost
servers = list(map(lambda x: f'apt{x}.apt.emulab.net', [137]))
clients = list(map(lambda x: f'apt{x}.apt.emulab.net', [141, 146, 147]))
# clients = list(map(lambda x: f'apt{x}.apt.emulab.net', [141]))
hosts = servers + clients

Cmds = {
	'sync': 'rsync -auv -e "ssh -o StrictHostKeyChecking=no" --exclude-from \'sync_exclude_list.txt\' ~/rdma_bench/ {user}@{host}:~/rdma_bench/',
	'run_server': '(cd ~/rdma_bench/herd && bash kill.sh; bash do.sh && bash run-servers.sh) &> log/{host}.log',
	# &> just does not work
	'run_client': 'ssh {user}@{host} "cd ~/rdma_bench/herd && bash kill.sh; bash do.sh && bash run-machine.sh {i}" > log/{host}.log 2> /dev/null',
    'kill': 'ssh {user}@{host} "cd ~/rdma_bench/herd && ./kill.sh"',
}

def signal_handler(sig, frame):
	print('kill all servers and clients')
	for h in hosts:
		print(f'kill {h}')
		ret = os.popen(Cmds['kill'].format(user=user, host=h)).read()
	sys.exit(0)

# non-blocking or blocking actually depends on whether cmd is bg or fg
def blocking_run(cmd):
	ret = os.popen(cmd).read()
	return ret

# always non-blocking, as it is running in a subprocess. 
def non_blocking_run(cmd):
    subprocess.Popen(['/bin/bash', '-c', cmd])

if __name__ == "__main__":	
	signal.signal(signal.SIGINT, signal_handler)
	
	for c in clients:
		print(f'syncing {c}')
		# blocking, as Cmds['sync'] is set to run in foreground
		ret = blocking_run(Cmds['sync'].format(user=user, host=c))
		# print(ret)

	for s in servers:
		non_blocking_run(Cmds['run_server'].format(host=s))

	print("waiting 2 seconds")
	time.sleep(2)

	for i, c in enumerate(clients):
		non_blocking_run(Cmds['run_client'].format(user=user, host=c, i=i))

	print("waiting for ctrl+c")
	signal.pause()