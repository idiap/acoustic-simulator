#!/usr/bin/python

#Copyright (c) 2015 Idiap Research Institute, http://www.idiap.ch/
#Written by Marc Ferras <marc.ferras@idiap.ch>,
#
#This file is part of AcSim.
#
#AcSim is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License version 3 as
#published by the Free Software Foundation.
#
#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with AcSim. If not, see <http://www.gnu.org/licenses/>.


import random
import sys
import os
import re
import glob
import argparse
from argparse import RawTextHelpFormatter
import signal
from functools import partial
#import random


def initRandom (file, seed):

	global rnd
	global rndidx

	rndidx = 0
	rnd=[]
	with open(file,'r') as f:
		for l in f.readlines():
			rnd.append(l.strip())

	if seed == '' or seed =='0':
		rndidx=0
	else:
		rndidx=int(seed)
	if rndidx >= len(rnd):
		rndidx = rndidx % len(rnd)

	return (rnd)

def getRandom(nvalues):

	global rndidx
	global rnd

	maxint=9223372036854775807

	out = int ( float(nvalues)*float(rnd[rndidx]) /float(maxint) )

	rndidx = rndidx + 1
	if rndidx==len(rnd):
		rndidx=0

	return out

def listShuffle(l):

	global rnd
	global rndidx

	idx = range(0,len(l))
	idxp = list(idx)
	for i in idx:
		ri1 = getRandom(len(l))
		itmp = idxp[i]
		idxp[i] = idxp[ri1]
		idxp[ri1] = itmp

	l2 = [ l[i] for i in idxp ]
	return (l2)

def randomChoice(l):

	global rnd
	global rndidx

	ri = getRandom(len(l))
	return l[ri]

def sigint_handler (signum, frame):
	print 'captured!'
	sys.exit(1)

def buildFileName (fileName,codecs):

	s = os.path.splitext(fileName)
	fileNoExt = s[0]
	ext=s[1]

	print ' '.join(codecs)
	codecs2=[]
	for c in codecs:
		if 'noise' in c:
			m=re.search(r'snr=([0-9]+)',c)
			if m:
				snr=m.group(1)
				c = 'noisy.snr' + snr
			else:
				c='noisy'

		codecs2.append(c)

	codecstr = '-'.join(codecs2)
	codecstr = re.sub('\|', '', codecstr)
	codecstr = re.sub('\\\\', '', codecstr)
	codecstr = re.sub('[\]=]', '', codecstr)
	codecstr = re.sub('[\[,]', '.', codecstr)
	codecstr = re.sub('/', '', codecstr)

	if len(codecs)>0:
		fileName = fileNoExt + '-' + codecstr + ext
	else:
		fileName = fileNoExt + ext
	return (fileName)

def fileEmpty (fileName):
	if os.path.exists(fileName):
		if (os.path.getsize(fileName))<=2:
			return True
		else:
			return False
	else:
		return True

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument("-s", dest="seed", default='0', help="Seed to initialize the random number generator")
parser.add_argument('condition',nargs='?', help="Acoustic condition ([nocodec|landline|cellular|satellite|voip|interview|playback].[clean|noisy08|noisy15]")
parser.add_argument("-D", dest="deviceirlist", default='ir-device-file-list.txt', help="Device impulse response file list")
parser.add_argument("-P", dest="spaceirlist", default='ir-space-file-list.txt', help="Space impulse response file list")
parser.add_argument("-N", dest="noiselist", default='noise-file-list.txt', help="Noise file list")
parser.add_argument('filelist',nargs='?',help="File list to process")
parser.add_argument('outdir',nargs='?')
options = parser.parse_args()

# initialize reproducible random number generator
initRandom('random', options.seed)


argcond=options.condition
if argcond=='-':
	argcond='all'
fileList=options.filelist
outDir=options.outdir


cmdFile='./degrade-audio-safe-random.py -D ' + options.deviceirlist + ' -P ' + options.spaceirlist + ' -N ' + options.noiselist
#cmdFile=''

signal.signal (signal.SIGINT,partial(sigint_handler))


#if len(sys.argv)!=4:
#	print 'Syntax: create-degraded-speech-feats.py cond audio-file-list outdir'
#	exit()

#argcond=sys.argv[1]
#if argcond=='-':
#	argcond='all'
#fileList = sys.argv[2]
#outDir = sys.argv[3]


noiseConditions = ['clean','ambience-babble', 'ambience-private', 'ambience-music', 'ambience-nature', 'ambience-transportation', 'ambience-outdoors', 'ambience-public', 'ambience-impulsive']
codecConditions=['nocodec','landline','cellular','satellite','voip','interview','playback']
#levels = [-26, -29, -32, -35]  # dbFS
#snrs = [25,20,15,10,5]
#snrsHVAC=[25,20,15]
levels = [-26, -29, -32, -35]  # dbFS
#snrs = [25,20,15,10]
#snrsHVAC=[25,20,15]
noiseTypes = ['ambience-babble', 'ambience-private', 'ambience-music', 'ambience-transportation', 'ambience-outdoors', 'ambience-public', 'ambience-impulsive']

codecsLandline = ['g711','g726']
codecsCellular = ['amr','amrwb','gsmfr']
codecsSatellite = ['g728','c2','cvsd']
codecsVoIP = ['silk','silkwb','g729a','g722']
codecsInterview = ['mp3','aac']
codecsPlayback = ['mp3','aac']
codecsBPFilter = ['g711','g726','amr','gsmfr', 'g728']

amrParms = ['amr[br=4k75]','amr[br=5k15]', 'amr[br=5k9]', 'amr[br=6k7]', \
						'amr[br=7k4]', 'amr[br=7k95]', 'amr[br=10k2]', 'amr[br=12k2]', \
						'amr[br=4k75,nodtx]','amr[br=5k9,nodtx]', 'amr[br=5k9,nodtx]', \
						'amr[br=6k7,nodtx]', 'amr[br=7k4,nodtx]', 'amr[br=7k95,nodtx]', \
						'amr[br=10k2,nodtx]']
amrwbParms = ['amrwb[br=6k6]','amrwb[br=12k65]', 'amrwb[br=15k85]', 'amrwb[br=23k05]', \
						'amrwb[br=6k6,nodtx]','amrwb[br=12k65,nodtx]', 'amrwb[br=15k85,nodtx]', 'amrwb[br=23k05,nodtx]']

g711Parms = ['g711[law=u]', 'g711[law=a]']
g726Parms = ['g726[law=u,br=16k]', 'g726[law=u,br=24k]', 'g726[law=u,br=32k]','g726[law=u,40k]',\
 						'g726[law=a,br=16k]', 'g726[law=a,br=24k]', 'g726[law=a,br=32k]','g726[law=a,br=40k]']
g729aParms = ['g729a']
g728Parms = ['g728']
g722Parms = ['g722[br=64k]', 'g722[br=56k]', 'g722[br=48k]']
gsmfrParms = [ 'gsmfr']
silkParms = ['silk[br=5k]','silk[br=10k]','silk[br=15k]','silk[br=20k]', \
						'silk[br=5k,loss=5]','silk[br=10k,loss=5]','silk[br=15k,loss=5]','silk[br=20k,loss=5]',\
						'silk[br=5k,loss=10]','silk[br=10k,loss=10]','silk[br=15k,loss=10]','silk[br=20k,loss=10]']
silkwbParms = ['silkwb[br=10k]','silkwb[br=20k]','silkwb[br=30k]', \
						'silkwb[br=10k,loss=5]','silkwb[br=20k,loss=5]','silkwb[br=30k,loss=5]',\
						'silkwb[br=10k,loss=10]','silkwb[br=20k,loss=10]','silkwb[br=30k,loss=10]']
bpParms = ['bp[ft=g712]','bp[ft=p341]','bp[ft=irs]','bp[ft=mirs]']
mp3Parms = ['mp3[8k]','mp3[16k]','mp3[32k]']
aacParms = ['aac[8k]','aac[16k]','aac[32k]']
c2Parms = ['c2[br=3k2]', 'c2[br=2k4]']
cvsdParms = ['cvsd[br=8k]', 'cvsd[br=16k]', 'cvsd[br=24k]', 'cvsd[br=32k]']

# read files to process
try:
	with open(fileList) as f:
		files = f.read().splitlines()
#		files = sorted(set(files))
except:
	print 'could not read file ' + fileList
	exit()

cond=''
ncond=''
ncondsnr=''
s=argcond.split('.')
if len(s)>0:
	cond=s[0]
if len(s)>1:
	if s[1]=='clean' or s[1]=='':
		ncond=''
	elif s[1]=='noisy08' or s[1]=='noisy15' or s[1]=='noisy25':
		ncond=s[1][:-2]
		ncondsnr=s[1][-2:]
	else:
		print 'the noisy condition should be either noisy08 or noisy15'
		sys.exit(0)


if cond!='' and ncond=='':
	print 'doing condition ' + cond + '(no noise condition)'
	outDirCond = outDir + '/' + cond
elif cond!='' and ncond!='':
	print 'doing condition ' + cond + '.' + ncond
	outDirCond = outDir + '/' + cond + '.' + ncond + ncondsnr

try:
	os.makedirs(outDirCond)
except:
	pass
	
fscp = open (outDirCond + '.scp','w')

if cond=='landline':
	for nf,f in enumerate(files):

		level = randomChoice(levels)
		codecList=['norm[rms='+ str(level) + ']']

		# additive noise
		if ncond != '':
			opt='noise[filter=ambience-public\|ambience-private\|ambience-outdoors\|ambience-babble\|ambience-transportation\|ambience-music,snr='+str(ncondsnr)+']'
			codecList.append(opt)

		# apply random landline codec
		codecList2 = []
		codec = randomChoice(codecsLandline)
		# apply band-pass filter first if needed
		if codec in codecsBPFilter:
			opt = randomChoice(bpParms)
			codecList2.append(opt)
		# apply codec
		parms=eval(codec+'Parms')
		opt=randomChoice(parms)
		codecList2.append(opt)

		codecs = codecList + codecList2
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), codecs)
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
		fscp.write (outputFile + '\n') 
		fscp.flush()
		print ''
		print ''
	fscp.close()

elif cond=='cellular':
	for nf,f in enumerate(files):
		level = randomChoice(levels)
		codecList=['norm[rms='+ str(level) + ']']
		# additive noise
		if ncond != '':
			opt='noise[filter=ambience-public\|ambience-private\|ambience-outdoors\|ambience-babble\|ambience-transportation\|ambience-music,snr='+str(ncondsnr)+']'
			codecList.append(opt)

		# apply random landline codec
		codecList2 = []
		codec = randomChoice(codecsCellular)
		# apply band-pass filter first if needed
		if codec in codecsBPFilter:
			opt = randomChoice(bpParms)
			codecList2.append(opt)
		# apply codec
		parms=eval(codec+'Parms')
		opt=randomChoice(parms)
		codecList2.append(opt)

		codecs = codecList + codecList2
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), codecs)
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
		fscp.write (outputFile + '\n') 
		fscp.flush()
		print ''
		print ''
	fscp.close()

elif cond=='satellite':
	for nf,f in enumerate(files):
		level = randomChoice(levels)
		codecList=['norm[rms='+ str(level) + ']']
		# additive noise
		if ncond != '':
			opt='noise[filter=ambience-public\|ambience-private\|ambience-outdoors\|ambience-babble\|ambience-transportation\|ambience-music,snr='+str(ncondsnr)+']'
			codecList.append(opt)

		# apply random landline codec
		codecList2 = []
		codec = randomChoice(codecsSatellite)
		# apply band-pass filter first if needed
		if codec in codecsBPFilter:
			opt = randomChoice(bpParms)
			codecList2.append(opt)
		# apply codec
		parms=eval(codec+'Parms')
		opt=randomChoice(parms)
		codecList2.append(opt)

		codecs = codecList + codecList2
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), codecs)
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
			print ''
			print ''
		fscp.write (outputFile + '\n') 
		fscp.flush()
	fscp.close()

elif cond=='voip':
	for nf,f in enumerate(files):
		level = randomChoice(levels)
		codecList=['norm[rms='+ str(level) + ']']
		# additive noise
		if ncond != '':
			opt='noise[filter=ambience-public\|ambience-private\|ambience-outdoors\|ambience-babble\|ambience-transportation\|ambience-music,snr='+str(ncondsnr)+']'
			codecList.append(opt)

		# apply random landline codec
		codecList2 = []
		codec = randomChoice(codecsVoIP)
		# apply band-pass filter first if needed
		if codec in codecsBPFilter:
			opt = randomChoice(bpParms)
			codecList2.append(opt)
		# apply codec
		parms=eval(codec+'Parms')
		opt=randomChoice(parms)
		codecList2.append(opt)

		codecs = codecList + codecList2
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), codecs)
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
			print ''
			print ''
		fscp.write (outputFile + '\n') 
		fscp.flush()
	fscp.close()


elif cond=='playback':

	for f in files:
		level = randomChoice(levels)
		codecList=['norm[rms='+ str(level) + ']']
		# additive noise
		if ncond != '':
			opt='noise[filter=ambience-public\|ambience-private\|ambience-outdoors\|ambience-babble\|ambience-transportation\|ambience-music,snr='+str(ncondsnr)+']'
			codecList.append(opt)

		# apply landline|cellular|voip codec + device impulse response + audio codec (mp3 or aac)
		codecList2 = []
		tmp = sum ([codecsLandline, codecsCellular, codecsVoIP],[])
		codec = randomChoice(tmp)
		if codec in codecsBPFilter:
			opt = randomChoice(bpParms)
			codecList2.append(opt)
		# apply codec
		parms=eval(codec+'Parms')
		opt=randomChoice(parms)
		codecList2.append(opt)

		opt='irdevice'
		codecList2.append(opt)
		codecAudio=randomChoice(codecsPlayback)
		parms=eval(codecAudio+'Parms')
		opt=randomChoice(parms)
		codecList2.append(opt)

		codecs = codecList + codecList2
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), codecs)
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
			print ''
			print ''
		fscp.write (outputFile + '\n') 
		fscp.flush()

	print ''
	fscp.close()

elif cond=='interview':

	for f in files:
		level = randomChoice(levels)
		codecList=['norm[rms='+ str(level) + ']']

		if ncond != '':
#			snr = randomChoice(snrsHVAC)
			opt='noise[filter=hvac,snr='+str(ncondsnr)+']'
			codecList.append(opt)

		# apply small room impulse response + audio codec (mp3 or aac)
#		opt='irspace[filter=small\|medium]'
		opt='irspace[filter=small/]'
		codecList.append(opt)

		codec=randomChoice(codecsInterview)
		parms=eval(codec+'Parms')
		opt=randomChoice(parms)
		codecList.append(opt)

		codecs = codecList
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), codecs)
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
			print ''
			print ''
		fscp.write (outputFile + '\n') 
		fscp.flush()

	fscp.close()

elif cond=='nocodec':
	# additive noise
	level = randomChoice(levels)
	codecList=['norm[rms='+ str(level) + ']']
	if ncond != '':
		opt='noise[filter=ambience-public\|ambience-private\|ambience-outdoors\|ambience-babble\|ambience-transportation\|ambience-music,snr='+str(ncondsnr)+']'
		codecList.append(opt)

	codecs = codecList

	for nf,f in enumerate(files):
		outputFile = outDirCond+'/'+buildFileName(os.path.basename(f), [])
		outputFile = os.path.splitext(outputFile)[0] + '.wav'
		if fileEmpty(outputFile):
			if options.seed == '':
				cmd = cmdFile + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			else:
				cmd = cmdFile + ' -s ' + str(rndidx) + ' -r 8000 -c ' + ':'.join(codecs) + ' ' + f + ' ' + outputFile
			print cmd
			os.system(cmd)
			print ''
			print ''
		fscp.write (outputFile + '\n') 
		fscp.flush()
	
	fscp.close()
