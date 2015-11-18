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


import os,sys,subprocess
import numpy as np
import scikits.audiolab as al  # audiolab, install through pip, requires libsndfile
import scikits.samplerate as src  # secret rabbit code resampled, install through pip, requires SRC
import matplotlib.pyplot as plt
import struct
import re

def loadSignal(fileName):
	try:
		x, Fs, encFmt = al.wavread(fileName)
	except IOError:
		print('Could not import file "%s"' % sigPath)
		return None

	return (x, Fs)

def find1(L, S):
	return [x for x in (L) if S in x]


irOriginal='impulse-responses-original'
irOutput='impulse-responses'
irDeviceList='ir-device-file-list.txt'
irSpaceList='ir-space-file-list.txt'

kwDevice = ['devices']
kwSpace = ['spaces']
kwBlockSpace = []

# read wav IR
swav=subprocess.check_output('find -L ' + irOriginal + ' -type f -name \"*.wav\"', shell=True)
swav=swav.split('\n')
swav=swav[:-1]

nDevice = 0
nSpace = 0 
fdevice=open(irDeviceList,'wt')
fspace=open(irSpaceList,'wt')
for ln in swav:
	(fileName, fileExtension) = os.path.splitext(ln)

	# read wav file
	(x,fs)=loadSignal(ln)
	sx=x.shape
	if len(sx)==2:
		ir = x[:,1]
	elif len(sx)==1:
		ir = x
	else:
		print 'too many channels for IR ' + ln + ': skipping'
		continue

	ir8k = src.resample(ir, 8000/float(fs), 'sinc_medium')
	ir8kabs = ir8k * ir8k
	sum8k=ir8kabs.sum()
	ir8k = ir8k / np.sqrt(sum8k)
	dname=os.path.dirname(ln)
	lin=dname.split('/')[1:]
	lout=[]
	for elem in lin:
		e = ''.join(e for e in elem if e.isalnum())
		lout.append(e)
	outdir=irOutput + '/' + '/'.join(lout)


	basename = os.path.basename(ln)
	basename = re.sub('.wav','',basename)
	basename = ''.join(e for e in basename if e.isalnum())

	basename8k = basename + '-8000.ir'
	outfile8k = outdir + '/' + basename8k

	ir16k = src.resample(ir, 16000/float(fs), 'sinc_medium')
	ir16kabs = ir16k * ir16k
	sum16k=ir16kabs.sum()
	ir16k = ir16k / np.sqrt(sum16k)
	basename16k = basename + '-16000.ir'
	outfile16k = outdir + '/' + basename16k

	foundSpace = False
	foundBlockSpace = False
	for kw in kwSpace:
		if kw in dname:
			foundSpace = True
			if foundSpace:
				for kw2 in kwBlockSpace:
					if kw2 in dname:
						foundBlockSpace = True
			if foundSpace and not foundBlockSpace:
				break
			elif foundSpace and foundBlockSpace:
				foundSpace = False

	foundDevice = False
	for kw in kwDevice:
		if kw in dname:
			foundDevice = True
			break

	if foundDevice:
		try:
			os.makedirs(outdir)
		except:
			pass
		print ln
		np.savetxt(outfile8k, ir8k, newline=' ')
		np.savetxt(outfile16k, ir16k, newline=' ')
		fdevice.write(outfile16k +'\n')
		nDevice = nDevice + 1

	if foundSpace:
		try:
			os.makedirs(outdir)
		except:
			pass
		print ln
		np.savetxt(outfile8k, ir8k, newline=' ')
		np.savetxt(outfile16k, ir16k, newline=' ')
		fspace.write(outfile16k +'\n')
		nSpace = nSpace + 1

fdevice.close()
fspace.close()

print str(nDevice) + ' device IRs'
print str(nSpace) + ' space IRs'
