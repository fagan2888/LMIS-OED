import multiprocessing as mp
from multiprocessing.pool import Pool
import subprocess
import random
import numpy as np
import os, sys, time, datetime
from common import *

executable = './build2/Driver'
if not os.path.isfile(executable[2:]):
  print "could not find executable"
  exit()

if sys.argv[1] == '2':
  dim, sigeps = 2, 0.1

if sys.argv[1] == '4':
  dim, sigeps = 4, 0.4

algorithms = ['exact']

evaluations = np.logspace(3, 6, 11)
M_values = map(int, np.floor(np.sqrt(evaluations / 10) / 2 + 0.5))
N_values = map(int, np.floor(np.sqrt(evaluations / 10) * 10 + 0.5))

design = 0.5

trials = 1000

options = {
  "-dim":dim,
  "-sigeps":sigeps,
  "-poi":1,
  "-design":design,
  "-seed":0,
  "-dumpfile":"none",
  "-outfile":"none",
  "-N":0,
  "-M1":0,
  "-M2":0,
  "-useIS":0,
  "-useMIS":0,
  "-useReverseLikelihood":1,
  "-useMinSampleDistance":0,
  "-sort":1,
  "-useExactPosterior":0,
  "-maxComponents":0,
  "-biasingDistributionType":"MVT",
  "-dof":2.5,
  "-nugget":1e-3}

runs = []

def get_run(N, M, algo):
  options['-N'] = N;
  options['-M1'] = M;
  options['-M2'] = M;
  options['-maxComponents'] = N;
  options['-useExactPosterior'] = 0
  options['-biasingDistributionType'] = 'MVT'
  if algo is 'prior':
    options['-useIS'], options['-useMIS'] = 0, 0
  if algo is 'is':
    options['-useIS'], options['-useMIS'] = 1, 0
  if algo is 'mis':
    options['-useIS'], options['-useMIS'] = 0, 1
  if algo is 'exact':
    options['-useIS'], options['-useMIS'] = 1, 0
    options['-useExactPosterior'] = 1
    options['-biasingDistributionType'] = 'MVN'
  filename = 'out/convergence_eval/eval%dd_%s_N%04d_M%04d' % (dim, algo, N, M)
  arguments = [executable]
  for k, v in options.iteritems():
    arguments.append('%s' % k)
    arguments.append('%s' % v)
  return {"filename":filename, "arguments":arguments}

for algo in algorithms:
  for trial in xrange(trials):
    for i in range(len(evaluations)):
      run = get_run(N_values[i], M_values[i], algo)
      runs.append(run)

random.shuffle(runs)

def execute(run):
  output = subprocess.check_output(run['arguments'])
  f = open(run['filename'], 'a')
  f.write(output)
  f.close()

pool = Pool(processes=mp.cpu_count())
result = pool.map_async(execute, runs, chunksize=1)
start_time = time.time()
while not result.ready():
  completed = len(runs) - result._number_left
  if completed > 0:
    eta = (time.time() - start_time) / completed * result._number_left / 60
    print '%6d left, ETA: %4.1f minutes' % (result._number_left, eta)
  sys.stdout.flush()
  time.sleep(1)

pool.close()

#nice parallel -j 6 --"command1""command2"
