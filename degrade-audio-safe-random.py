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

import argparse
from argparse import RawTextHelpFormatter
import os,sys,subprocess
import re
import random
from math import ceil
import inspect
import math
import string

scriptDir=os.path.dirname(os.path.abspath (inspect.stack()[0][1]))

srcDir='.'

qioDir=srcDir+'/'+'src/aurora-front-end/qio/src'
qioBin=qioDir + '/nr'
fantBin=srcDir+'/'+'src/fant/filter_add_noise'
g711bin=srcDir+'/'+'src/Software/stl2009/g711/g711demo'
g726bin=srcDir+'/'+'src/Software/stl2009/g726/g726demo'
g722bin=srcDir+'/'+'src/Software/stl2009/g722/g722demo'
g728bin=srcDir+'/'+'src/Software/stl2009/g728/g728fixed/g728fp'
g729aEncBin=srcDir+'/'+'src/Software/G729_Release3/g729AnnexA/c_code/coder'
g729aDecBin=srcDir+'/'+'src/Software/G729_Release3/g729AnnexA/c_code/decoder'
amrNBEncBin=srcDir+'/'+'src/amr-nb/encoder'
amrNBDecBin=srcDir+'/'+'src/amr-nb/decoder'
amrWBEncBin=srcDir+'/'+'src/G722-2AnxC-v.7.1.0/c-code-v.7.1.0/coder'
amrWBDecBin=srcDir+'/'+'src/G722-2AnxC-v.7.1.0/c-code-v.7.1.0/decoder'
silkBin=srcDir+'/'+'src/opus-1.1/opus_demo'
#ffmpegBin=srcDir+'/'+'src/ffmpeg-2.6.2/ffmpeg'
ffmpegBin='/usr/bin/ffmpeg'
soxBin=srcDir+'/'+'src/sox-14.4.2/src/sox -V1'
sph2pipeBin=srcDir+'/'+'src/sph2pipe_v2.5/sph2pipe'
c2EncBin=srcDir+'/'+'src/codec2/build_linux/src/c2enc'
c2DecBin=srcDir+'/'+'src/codec2/build_linux/src/c2dec'

codecStr='\n \
\n\'noise[opts]\': Add noise (opts: filter=keyword, snr=snr(dB), irspace=keyword, wet=(0-100))\n \
\n\'norm[opts]\': RMS power normalization (opts: rms=power(dBFS)\n \
\n\'nr[opts]\': Qualcomm-ICSI-OGI noise reduction (opts: type=fft|mel)\'\n \
\n\'bp[opts]\': Telephone band-pass filter (opts: ft=g712|p341|irs|mirs)\n \
\n\'irdevice[opts]\': Apply device impulse response (opts: filter=keyword)\n \
\n\'irspace[opts]\': Apply room impulse response (opts: wet=(0-100), filter=keyword)\n \
\n\'g711[opts]\': mu/A-law, 300-3400Hz, 64kbps, POTS (opts: law=u|a (mu-law|A-law)\n \
\n\'g726[opts]\': mu/A-law+ADPCM, 300-3400Hz, 32kbps, Phone Network, DECT (opts: law=u|a (mu-law|A-law), br=40k|32k|24k|16k)\n \
\n\'g722[opts]\': Wideband SB-ADPCM, 50-7000Hz, VoIP (opts: br=64k|56k|48k)\n \
\n\'g728[opts]\': Low-Delay CELP, 16kbps, Satellite (opts: lloss=(ms of packet loss))\n \
\n\'g729a\': CS-ACELP, 8kbps, low complexity, VoIP\n \
\n\'c2\': Codec2, low bit-rate radio & satellite (opts: br=3k2|2k4|1k4|1k3|1k2)\n \
\n\'cvsd[opts]\': Continuous Variable Slope Delta, Satellite radio, Bluetooth (opts: br=8k-64k)\n \
\n\'amr[opts]\': Adaptive Multirate, Cellular (opts: nodtx,br=4k75|5k15|5k9|6k7|7k4|7k95|10k2|12k2)\n \
\n\'amrwb[opts]\': Adaptive Multirate Wideband, Cellular (opts: nodtx,br=6k6|8k85|12k65|14k25|15k85|18k25|19k85|23k05|23k85)\n \
\n\'gsmfr\': Full-rate GSM, Cellular\n \
\n\'silk[opts]\': Narrow Band VoIP, Skype (opts: nodtx, br=5k-20k, loss=0-100)\n \
\n\'silkwb[opts]\': Wide Band VoIP, Skype (opts: nodtx, br=8k-30k, loss=0-100)\n \
\n\'mp3[opts]\': MPEG Layer 3, Audio (opts: br=8k-128k)\n \
\n\'aac[opts]\': Advanced Audio Codec, Audio(opts: br=8k-128k)'

#codecsWithBP=[ 'g726', 'g711']
codecsWithBP=[]

amrOptions = ['nodtx','4k75','5k9','6k7','7k4','7k95','10k2','12k2','4750','5900','6700','7400','7950','10200','12200']
gsmhrOptions = ['nodtx']
gsmEFROptions = ['nodtx']
silkOptions = ['nodtx']
silkWBOptions = ['nodtx']
amrWBOptions = ['nodtx','6k6','8k85','12k65','14k25','15k85','18k25','19k85','23k05','23k85','6600','8850','12650','14250','15850','18250','19850','23050','23850']
evrcOptions = ['nodtx']
g711Options = ['u','a']
g726Options = ['40k','32k','24k','16k','40000','32000','24000','16000']
g722Options = ['64k','56k','48k','64000','56000','48000']
c2Options = ['3k2','2k4','1k4','1k3','1k2']
bpOptions = ['g712','p341','irs','mirs']
nrOptions = ['fft','mel']


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


def br2int(s):
	if 'k' in s:
		l = s.split('k')
		if len(l)==1:
			br = int(l[0])*1000
		elif len(l)==2:
			if len(l[1])==0:
				br2 = 0
			elif len(l[1])==1:
				br2 = int(l[1]) * 100
			elif len(l[1])==2:
				br2 = int(l[1]) * 10
			elif len(l[1])==3:
				br2 = int(l[1])
			else:
				print 'cannot read bit-rate ' + s
				exit()
			br = int(l[0])*1000 + br2
	else:
		br = int(s)
	return (br)

def isBitRate (s):
	if ('k' in s) or s.isdigit():
		return True
	else:
		return False

def isNumber (s):
	if s.isdigit():
		return True
	else:
		return False

def isFloat (s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def isNarrowBand(codec, opts):
	c = {'g711' : 1,
			'g726' : 1,
			'g722' : -1,
			'g728' : 1,
			'g729a' : 1,
			'c2' : 1,
			'cvsd' : 0,
			'gsmhr': 1,
			'gsmfr' : 1,
			'gsmefr' : 1,
			'amr' : 1,
			'amrwb' : -1,
			'evrc' : 1,
			'evrcwb' : -1,
			'silk' : 1,
			'silkwb' : -1,
			'mp3' : 0,
			'aac' : 0,
			'nr' : 0,
			'bp' : 0,
			'irdevice' : 0,
			'irspace' : 0,
			'noise' : 0,
			'norm' : 0,
			'' : False,
	}

	try:
		return(c[codec])
	except:
		return(False)

	

def codecParse(codecStr):

	s = codecStr.split('[')
	if len(s)>0:
		codec = s[0]
		if len(s)>1:
			s[1]=s[1][:-1]
			opts = s[1].split(',')
		else:
			opts = []

	return (codec, opts)

def getCodecs(options):
	c = {'g711' : True,
			'g726' : True,
			'g722' : True,
			'g728' : True,
			'g729a' : True,
			'c2' : True,
			'cvsd' : True,
			'gsmfr' : True,
			'gsmefr' : False,
			'amr' : False,
			'amrwb' : False,
			'evrc' : False,
			'evrcwb' : False,
			'silk' : True,
			'silkwb' : True,
			'mp3' : True,
			'aac' : True,
			'nr' : False,
			'bp' : True,
			'irdevice' : True,
			'irspace' : True,
			'noise' : True,
			'norm' : True,
	}

	codecstr = options.codec.split(':')
	lcodecs = []
	lopts = []
	for codec in codecstr:
		(codec,opts) = codecParse(codec)
		try:
			c[codec]
			lcodecs.append(codec)
		except:
			if len(codec)>0:
				print 'codec ' + codec + ' not supported. Allowed codecs are: ' +codecStr+'.'
				exit()
			else:
				# no codec specified. go on
				return([],[])

		if codec=='norm':
			dopts= {'rms' : -26}
			for opt in opts:
				opt = opt.lower()
				if opt[:4]=='rms=':
					dopts ['rms'] = opt[4:]
					continue
				else:
					print 'option ' + opt + ' not recognized: skipping'


		# check options for amr
		if codec=='amr':
			dopts= {'bit-rate' : '10k2', 'dtx': True}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
 				elif opt[:3]=='br=':
 					if isBitRate(opt[3:]) and (opt[3:] in amrOptions):
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[amr]: option ' + opt + ' not recognized: skipping'

		if codec=='silk':
			dopts= {'bit-rate' : '10k', 'dtx': True, 'loss': 0}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
				elif opt[:5]=='loss=':
					dopts['loss'] = opt[5:]
 				elif opt[:3]=='br=':
 					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<5000 or br>20000:
							print '[silk]: bit-rate must be in the range [5000,20000]'
							exit()
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[silk]: option ' + opt + ' not recognized: skipping'

		if codec=='mp3':
			dopts= {'bit-rate' : '32k'}
			for opt in opts:
				opt = opt.lower()
 				if opt[:3]=='br=':
 					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<8000 or br>128000:
							print '[mp3]: bit-rate must be in the range [8000,128000]'
							exit()
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[mp3]: option ' + opt + ' not recognized: skipping'

		if codec=='aac':
			dopts= {'bit-rate' : '32k'}
			for opt in opts:
				opt = opt.lower()
 				if opt[:3]=='br=':
 					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<8000 or br>128000:
							print '[aac]: bit-rate must be in the range [8000,128000]'
							exit()
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[aac]: option ' + opt + ' not recognized: skipping'


		if codec=='silkwb':
			dopts= {'bit-rate' : '20k', 'dtx': True, 'loss': 0}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
				elif opt[:5]=='loss=':
					dopts['loss'] = opt[5:]
 				elif opt[:3]=='br=':
 					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<8000 or br>30000:
							print '[silk]: bit-rate must be in the range [8000,30000]'
							exit()
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[silk]: option ' + opt + ' not recognized: skipping'

		if codec=='bp':
			dopts= {'bp-type' : 'g712'}
			for opt in opts:
				opt = opt.lower()
				if opt[:3]=='ft=':
					if opt[3:] in bpOptions:
						dopts ['bp-type'] = opt[3:]
						continue
					else:
						print 'option ' + opt + ' not recognized: skipping'
				else:
					print 'option ' + opt + ' not recognized: skipping'

		if codec=='nr':
			dopts= {'type' : 'fft'}
			for opt in opts:
				opt = opt.lower()
				if opt[:5]=='type=':
					if opt[5:] in nrOptions:
						dopts ['type'] = opt[5:]
						continue
					else:
						print 'option ' + opt + ' not recognized: skipping'
				else:
					print 'option ' + opt + ' not recognized: skipping'

		if codec=='cvsd':
			dopts= {'bit-rate' : '24k'}
			for opt in opts:
 				if opt[:3]=='br=':
 					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<8000 or br>64000:
							print '[cvsd]: sampling frequency must be in the range [8000,64000]'
							exit()
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[cvsd]: option ' + opt + ' not recognized: skipping'

		if codec=='evrc':
			dopts= {'dtx': True, 'bit-rate': '10k'}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
 				elif opt[:3]=='br=':
					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<5000 or br>20000:
							print '[evrc]: sampling frequency must be in the range [5000,20000]'
							exit()
						dopts['bit-rate'] = opt[3:]
	 					continue
					else:
						print 'option ' + opt + ' not recognized: skipping'

		if codec=='g729a':
			dopts= {}

		if codec=='gsmhr':
			dopts= {'dtx': True}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
				else:
					print 'option ' + opt + ' not recognized: skipping'

		if codec=='gsmefr':
			dopts= {'dtx': True}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
				else:
					print 'option ' + opt + ' not recognized: skipping'

		if codec=='gsmfr':
			dopts= {}

		if codec=='evrcwb':
			dopts= {'dtx': True, 'bit-rate': '20k'}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
 				elif opt[:3]=='br=':
					if isBitRate(opt[3:]):
						br=br2int(opt[3:])
						if br<8000 or br>30000:
							print '[evrcwb]: sampling frequency must be in the range [8000,30000]'
							exit()
						dopts['bit-rate'] = opt[3:]
	 					continue
					else:
						print 'option ' + opt + ' not recognized: skipping'
				else:
					print 'option ' + opt + ' not recognized: skipping'

		if codec=='amrwb':
			dopts= {'bit-rate' : '18k25', 'dtx': True}
			for opt in opts:
				opt = opt.lower()
				if opt=='nodtx':
					dopts ['dtx'] = False
					continue
 				elif opt[:3]=='br=':
 					if isBitRate(opt[3:]) and (opt[3:] in amrWBOptions):
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[amr]: option ' + opt + ' not recognized: skipping'

		# check options for g711
		if codec=='g711':
			dopts = {'law': 'u'}
			for opt in opts:
				opt = opt.lower()
				if opt[0:4]=='law=':
 					if opt[4:] in g711Options:
 						dopts['law'] = opt[4:]
					else:
						print '[g711]: option ' + opt + ' not recognized: skipping'
				else:
					print '[g711]: option ' + opt + ' not recognized: skipping'

		if codec=='g726':
			dopts={'law': 'u', 'bit-rate': '32k'}
			for opt in opts:
				opt = opt.lower()
				if opt[:4]=='law=':
					if opt[4:] in g711Options:
						dopts['law'] = opt[4:]
						continue
					else:
						print '[g726]: option ' + opt + ' not recognized: skipping'
				elif opt[:3]=='br=':
					if isBitRate(opt[3:]) and (opt[3:] in g726Options):
						dopts['bit-rate'] = opt[3:]
						continue
					else:
						print '[g726]: option ' + opt + ' not recognized: skipping'

		if codec=='g722':
			dopts={'bit-rate': '56k'}
			for opt in opts:
				opt = opt.lower()
 				if opt[:3]=='br=':
 					if isBitRate(opt[3:]) and (opt[3:] in g722Options):
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[g722]: option ' + opt + ' not recognized: skipping'

		if codec=='g728':
			dopts={'lloss': 0}
			for opt in opts:
				opt = opt.lower()
 				if opt[:6]=='lloss=':
 					if isFloat(opt[6:]):
						if float(opt[6:])>=2.5 and float(opt[6:])<=20:
							dopts['lloss'] = float(opt[6:])
 							continue
						else:
							print 'packet loss length not in the range [2.5,20] ms: skipping'
 					else:
 						print '[g728]: option ' + opt + ' not recognized: skipping'

		if codec=='c2':
			dopts={'bit-rate': '3k2'}
			for opt in opts:
				opt = opt.lower()
 				if opt[:3]=='br=':
 					if isBitRate(opt[3:]) and (opt[3:] in c2Options):
						dopts['bit-rate'] = opt[3:]
 						continue
 					else:
 						print '[c2]: option ' + opt + ' not recognized: skipping'

		if codec=='irdevice':
			dopts={'wet': 100, 'filter': ''}
			for opt in opts:
				optl = opt.lower()
				if optl[0:7]=='filter=':
					dopts ['filter'] = opt[7:]
					continue
				else:
					print '[irdevice]: option ' + opt + ' not recognized: skipping'

		if codec=='irspace':
			dopts={'wet': 100, 'filter': ''}
			for opt in opts:
				optl = opt.lower()
				if optl[:4]=='wet=':
					if int(optl[4:])<0 or int(optl[4:])>100:
						print '[irspace]: wet should be in the range [0,100]'
						exit()
					dopts['wet'] = optl[4:]
				elif optl[0:7]=='filter=':
					dopts ['filter'] = opt[7:]
					continue
				else:
					print '[irspace]: option ' + opt + ' not recognized: skipping'

		if codec=='noise':
			dopts= {'filter' : '', 'snr': -20, 'irspace': '', 'wet': 100}
			for opt in opts:
				optl = opt.lower()
				if optl=='space':
					dopts ['space'] = True
					continue
				elif optl[0:4]=='snr=':
					if float(optl[4:])<-100 or float(optl[4:])>100:
						print '[noise]: snr should be in the range [-100,100] dB'
						exit()
					dopts['snr'] = float(optl[4:])
				elif optl[0:7]=='filter=':
					dopts ['filter'] = opt[7:]
					continue
				elif optl[0:8]=='irspace=':
					dopts ['irspace'] = opt[8:]
					continue
				elif optl[:4]=='wet=':
					if int(optl[4:])<0 or int(optl[4:])>100:
						print '[noise]: irspace wet should be in the range [0,100]'
						exit()
					dopts['wet'] = optl[4:]
				else:
					print '[noise]: option ' + opt + ' not recognized: skipping'


		lopts.append(dopts)

	return (lcodecs,lopts)

def readNoiseTypes(file):
	l=[]
	try:
		with open(file) as f:
			for ln in f:
				ln = ln.strip('\n')
				ln = re.sub (r'.*\/','',ln)
				l.append(ln)
		return(l)
	except:
		return(l)

def readIRs(file):
	l=[]
	try:
		with open(file) as f:
			for ln in f:
				ln = ln.strip('\n')
				l.append(ln)
		return(l)
	except:
		return(l)


def readNoiseFiles(file):
	l=[]
	try:
		with open(file) as f:
			for ln in f:
				ln = ln.strip('\n')
				l.append(ln)
		return(l)
	except:
		return(l)

def filterPick(lines, regex):
	matches = map(re.compile(regex).match, lines)
	return [m.group(0) for m in matches if m]

def getAudioStats(filename,soxopts=''):
	s=subprocess.check_output(soxBin+' ' + soxopts + ' ' + filename + ' -n stat 2>&1', shell=True)
	s=s.split('\n')
	for ln in s:

		m=re.search(r'Samples read:\s+([0-9]+)',ln)
		if m:
			nSamples=m.group(1)
			continue

		m=re.search(r'Length \(seconds\):\s+([0-9]+\.[0-9]+)',ln)
		if m:
			lengthSec=m.group(1)
			continue

		m=re.search(r'RMS\s+amplitude:\s+([0-9]+\.[0-9]+)',ln)
		if m:
			rmsAmplitude=m.group(1)
			continue

	return (int(nSamples),float(lengthSec), float(rmsAmplitude))

def getSpeechRMSAmp(filename,soxopts=''):
	tmp=tmpDir +'/' + os.path.basename(filename) +'-getSpeechRMSAmp.raw'
	os.system(soxBin+' ' + soxopts + ' ' + filename + ' ' + tmp + ' vad ')
	if os.path.getsize(tmp)>0:
		s=subprocess.check_output(soxBin+' ' + soxopts + ' ' + tmp + ' -n stat 2>&1', shell=True)
		os.system('rm -f ' + tmp)
		s=s.split('\n')
		for ln in s:

			m=re.search(r'RMS\s+amplitude:\s+([0-9]+\.[0-9]+)',ln)
			if m:
				rmsAmplitude=m.group(1)
				continue
	else:
		# run without vad
		s=subprocess.check_output(soxBin+' ' + soxopts + ' ' + filename + ' -n stat 2>&1', shell=True)
		s=s.split('\n')

		for ln in s:

			m=re.search(r'RMS\s+amplitude:\s+([0-9]+\.[0-9]+)',ln)
			if m:
				rmsAmplitude=m.group(1)
				continue

	return float(rmsAmplitude)




parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument("-r", dest="samplerate", default='auto', help="Force output sample rate")
parser.add_argument("-d", dest="showdeviceirs", default=False, action='store_true', help="Show list of devide impulse responses")
parser.add_argument("-D", dest="usedeviceirlist", default=scriptDir+'/'+'ir-device-file-list.txt', help="Device impulse response file list")
parser.add_argument("-p", dest="showspaceirs", default=False, action='store_true', help="Show list of space impulse responses")
parser.add_argument("-P", dest="usespaceirlist", default=scriptDir+'/'+'ir-space-file-list.txt', help="Space impulse response file list")
parser.add_argument("-s", dest="seed", default='0', help="Random seed")
parser.add_argument("-n", dest="shownoises", default=False, action='store_true', help="Show list of noise files")
parser.add_argument("-N", dest="usenoiselist", default=scriptDir+'/'+'noise-file-list.txt', help="Noise file list")
parser.add_argument("-c", dest="codec", default='', help="Supported algorithms: "+ codecStr +".\n\nAlgorithms can be cascaded, e.g. \'nr:bp[irs]:amr[nodtx,4k75]:gsmefr:mp3[8k]\'")
parser.add_argument("-g", dest="debug", default=False, action='store_true',help="Keep temporary files to help debug errors")
parser.add_argument('inputFile',nargs='?')
parser.add_argument('outputFile',nargs='?')
options = parser.parse_args()

# initialize reproducible random number generator
initRandom('random', options.seed)

noiseFiles=[]
if options.shownoises:
#	noiseFiles = readNoiseFiles(scriptDir+'/'+'noise-file-list.txt')
	noiseFiles = readNoiseFiles(options.usenoiselist)
	print 'read ' + str(len(noiseFiles)) + ' noise files'
	print '\n'.join(noiseFiles)
	sys.exit(0)


deviceIRs=[]
if options.showdeviceirs:
	deviceIRs = readIRs(options.usedeviceirlist)
#	deviceIRs = readIRs(scriptDir+'/'+'ir-device-file-list.txt')
	print 'read ' + str(len(deviceIRs)) + ' device impulse reponses'
	print '\n'.join(deviceIRs)
	sys.exit(0)

spaceIRs=[]
if options.showspaceirs:
	spaceIRs = readIRs(options.usespaceirlist)
#	spaceIRs = readIRs(scriptDir+'/'+'ir-space-file-list.txt')
	print 'read ' + str(len(spaceIRs)) + ' space impulse reponses'
	print '\n'.join(spaceIRs)
	sys.exit(0)

#if len(options.codec)==0:
#	exit()
(lcodecs,lopts)=getCodecs(options)

for codec in lcodecs:
	if codec=='noise' and len(noiseFiles)==0:
		noiseFiles = readNoiseFiles(options.usenoiselist)
#		noiseFiles = readNoiseFiles(scriptDir+'/'+'noise-file-list.txt')
		print 'read ' + str(len(noiseFiles)) + ' noise files'
		break

for codec in lcodecs:
	if codec=='irdevice' or options.showdeviceirs:
		deviceIRs = readIRs(options.usedeviceirlist)
#		deviceIRs = readIRs(scriptDir+'/'+'ir-device-file-list.txt')
		print 'read ' + str(len(deviceIRs)) + ' device impulse reponses'
		if options.showdeviceirs:
			'\n'.join(decideIRs)
		break

for codec in lcodecs:
	if codec=='irspace' or options.showspaceirs:
		spaceIRs = readIRs(options.usespaceirlist)
#		spaceIRs = readIRs(scriptDir+'/'+'ir-space-file-list.txt')
		print 'read ' + str(len(spaceIRs)) + ' space impulse reponses'
		if options.showspaceirs:
			'\n'.join(spaceIRs)
		break

inputFile = options.inputFile
outputFile = options.outputFile
fileIn=inputFile

if options.debug:
	print 'keeping all temporary files for debug'
rmTmp=not options.debug
tmpDir='tmp/' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

try:
	os.makedirs(tmpDir)
except:
	pass

stepNo=0
if options.seed == '':
	random.seed()
else:
	random.seed(int(options.seed))


fext = os.path.splitext (fileIn)[1]

fileInRaw=re.sub(fext,'.raw', tmpDir + '/' + os.path.basename(fileIn))
fileInRawIni=fileInRaw
fileOutRaw=''
# upsample to 16ksps if needed
if fext=='.sph':
	fileInWavTmp=re.sub('.raw','-tmp.wav', fileInRaw)
	os.system(sph2pipeBin+' -p -f rif -c 1 ' + fileIn + ' ' + fileInWavTmp + ' > /dev/null 2> /dev/null')
	os.system(soxBin+' ' + fileInWavTmp + ' -G -V0 -r 16000 -c 1 ' + fileInRaw + ' rate -h < /dev/null')
	os.system('rm -f ' + fileInWavTmp)
else:
	os.system(soxBin+' ' + fileIn + ' -G -V0 -r 16000 -c 1 ' + fileInRaw + ' rate -h < /dev/null')

# apply codecs
fileInRate=16000
for codec,opts in zip(lcodecs,lopts):

	print '\napplying ' + codec
	fileInRawCodec=re.sub('.raw','-'+str(stepNo)+'-tmp0-'+codec+'.raw',fileInRaw)
	if isNarrowBand(codec,opts)==1:
		if fileInRate==16000:
			# resample to 8ksps
			print '  narrow-band codec: resampling to 8ksps'
#			os.system(soxBin+' -t raw -e signed-integer -b 16 -r 16000 -c 1 ' + fileInRaw + ' -r 8000 ' + fileInRawCodec + ' < /dev/null')
			os.system(soxBin+' -t raw -e signed-integer -b 16 -r 16000 ' + fileInRaw + ' -G -r 8000 ' + fileInRawCodec + ' < /dev/null')
		else:
			os.system('cp ' + fileInRaw + ' ' + fileInRawCodec)
		fileInRate=8000
	elif isNarrowBand(codec,opts)==-1:
		if fileInRate==8000:
			# resample to 8ksps
			print '  wide-band codec: resampling to 16ksps'
#			os.system(soxBin+' -t raw -e signed-integer -b 16 -r 8000 -c 1 ' + fileInRaw + ' -r 16000 ' + fileInRawCodec + ' < /dev/null')
			os.system(soxBin+' -t raw -e signed-integer -b 16 -r 8000 ' + fileInRaw + ' -G -r 16000 ' + fileInRawCodec + ' < /dev/null')
		else:
			os.system('cp ' + fileInRaw + ' ' + fileInRawCodec)
		fileInRate=16000
	else:
		# 8000 and 16000 are fine
		os.system('cp ' + fileInRaw + ' ' + fileInRawCodec)

	if len(codec)==0:
		break

	#encode
	stepNo = stepNo + 1
	fileOutTmp1Raw=re.sub('.raw','-'+str(stepNo)+'-tmp1-'+codec+'.raw',fileInRaw)
	fileOutTmp2Raw=re.sub('.raw','-'+str(stepNo)+'-tmp2-'+codec+'.raw',fileInRaw)
	fileOutTmp3Raw=re.sub('.raw','-'+str(stepNo)+'-tmp3-'+codec+'.raw',fileInRaw)
	fileOutTmp4Raw=re.sub('.raw','-'+str(stepNo)+'-tmp4-'+codec+'.raw',fileInRaw)
	fileOutRaw=re.sub('.raw','-'+str(stepNo)+'-codec-'+codec+'.raw',fileInRaw)

	#encode and decode to fileOutDecRaw

	if codec=='noise':
		skip=False
		print '  adding noise (' + str(opts) + ')'
		if len(noiseFiles)>0:
				if len(opts['filter'])>0:
					s = opts['filter'].split('|')
					rexp = '.*'+opts['filter']+'.*'
					if len(s) == 1:
						l = filterPick (noiseFiles,rexp)
					else:
						rexp = '('
						for i,x in enumerate(s):
							if i != len(s)-1 :
								rexp = rexp + '.*'+x+'.*|'
							else:
								rexp = rexp + '.*'+x+'.*'
						rexp = rexp + ')'
						l = filterPick (noiseFiles,rexp)
				else:
					rexp = '.*'+opts['filter']+'.*'
					l = filterPick (noiseFiles,rexp)

				if len(l)>1:
					print '  ' + str(len(l)) + ' files matching ' + rexp + ', choosing one randomly'
				elif len(l)==1:
					print '  only 1 file matching ' + rexp
				else:
					print '  no files matching ' + rexp + ': skipping adding noise'
					skip=True

				if skip:
					os.system ('cp ' + fileInRawCodec + ' ' + fileOutTmp4Raw)
				else:
					(sampInputFile,lenInputFile,rmsInputFile)=getAudioStats(fileInRawCodec, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))
					rmsInputFile=getSpeechRMSAmp(fileInRawCodec, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))
#					random.shuffle(l)
					l=listShuffle(l)
					noiseFile=scriptDir+'/'+l[0]
					print '  using ' + noiseFile
					(sampNoiseFile,lenNoiseFile, rmsNoiseFile)=getAudioStats(noiseFile, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))
					rmsNoiseFile=getSpeechRMSAmp(noiseFile, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))
					repeatTimes=int(ceil(lenInputFile/lenNoiseFile))
					if repeatTimes>1:
						os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + noiseFile + ' ' + fileOutTmp1Raw + ' repeat ' + str(repeatTimes))
						os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp2Raw + ' trim 0 ' + str(lenInputFile))
					else:
						os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + noiseFile + ' ' + fileOutTmp2Raw + ' trim 0 ' + str(lenInputFile))

					noiseScaling=rmsInputFile/rmsNoiseFile
					print '  applying gain ' + '%.2f' % noiseScaling + ' to noise to match recording RMS power'
					noiseScaling=noiseScaling*pow(10,-float(opts['snr'])/20.0)
					print '  applying ' + '%.2f' % -float(opts['snr']) + ' gain to noise'
					os.system(soxBin+' -m -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileInRawCodec + ' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + str(noiseScaling) + ' '  + fileOutTmp2Raw + ' ' + fileOutTmp4Raw)

	elif codec=='irdevice' or codec=='irspace':
		skip=False

		if codec=='irdevice':
			print '  device IR (' + str(opts) + ') '
		elif codec=='irspace':
			print '  space IR (' + str(opts) + ') '
		rexp = '.*'+opts['filter']+'.*'
		if codec=='irdevice':
			l = filterPick (deviceIRs,rexp)
		elif codec=='irspace':
			s = opts['filter'].split('|')
			if len(s) == 1:
				l = filterPick (spaceIRs,rexp)
			else:
				rexp = '('
				for i,x in enumerate(s):
					if i != len(s)-1 :
						rexp = rexp + '.*'+x+'.*|'
					else:
						rexp = rexp + '.*'+x+'.*'
				rexp = rexp + ')'
				l = filterPick (spaceIRs,rexp)

		if len(l)>1:
			print '  ' + str(len(l)) + ' files matching ' + rexp + ', choosing one randomly'
		elif len(l)==1:
			print '  only 1 file matching ' + rexp
		else:
			print '  no files matching ' + rexp + ': skipping impulse response simulation'
			skip=True

		if skip:
			os.system ('cp ' + fileInRawCodec + ' ' + fileOutTmp4Raw)
		else:
#			random.shuffle(l)
			l=listShuffle(l)
			if fileInRate==16000:
				ir=scriptDir+'/'+l[0]
			elif fileInRate==8000:
				ir=scriptDir+'/'+re.sub('16000','8000',l[0])
			else:
				print '  only 8ksps and 16ksps IR supported: skipping'
				continue
		
			print '  using ' + ir
	
			rmsPreFIR=getSpeechRMSAmp(fileInRawCodec, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))	
			os.system(soxBin+' -G -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileInRawCodec + ' ' + fileOutTmp3Raw + ' fir ' + ir)
			rmsPostFIR=getSpeechRMSAmp(fileOutTmp3Raw, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))
			firScaling=rmsPreFIR / rmsPostFIR
			os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + str(firScaling) + ' ' + fileOutTmp3Raw + ' ' + fileOutTmp2Raw)

			if opts['wet']==100:
				os.system('cp ' + fileOutTmp2Raw + ' ' + fileOutTmp4Raw)
			else:
				gWet=str(float(opts['wet'])/100.0)
				gDry=str((100-float(opts['wet']))/100.0)
				print soxBin+' -m -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + gDry + ' ' + fileInRawCodec + ' -G -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + gWet + ' ' + fileOutTmp2Raw + ' ' + fileOutTmp4Raw
				os.system(soxBin+' -m -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + gDry + ' ' + fileInRawCodec + ' -G -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + gWet + ' ' + fileOutTmp2Raw + ' ' + fileOutTmp4Raw)
			
	elif codec=='norm':
		print '  normalizing audio (' + str(opts) + ')'
		rmsFile=getSpeechRMSAmp(fileInRawCodec, '-t raw -e signed-integer -b 16 -r ' + str(fileInRate))
		rmsTarget=pow( 10, float(opts['rms'])/20.0 )
		gain=rmsTarget/rmsFile
		print '  applying gain ' + '%.2f' % gain + ' to match ' + str(opts['rms']) + 'dbFS RMS power'
		os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' -v ' + str(gain) + ' ' + fileInRawCodec + ' ' + fileOutTmp4Raw)

	elif codec=='nr':
		print '  applying Qualcomm-OGI noise reduction (' + str(opts) + ')'
		os.environ["AURORACALC"]=qioDir
		os.system(qioBin + ' -swapin 0 -swapout 0 -fs ' + str(fileInRate) + ' -Stype QIO_'+opts['type'].upper()  + ' -i ' + fileInRawCodec + ' -o ' + fileOutTmp4Raw + ' 2> nr.log')

	elif codec=='bp':
		skip=False
		for c in lcodecs:
			if c in codecsWithBP:
				print '  skipping band-pass filtering: codec ' + c + ' already applies appropriate filtering.'
				skip=True

		if skip:
			os.system('cp ' + fileInRawCodec + ' ' + fileOutTmp4Raw)
		else:

			print '  applying band-pass filter',
			if opts['bp-type']=='g712':
				print 'G.712 (300-3400Hz)'
			elif opts['bp-type']=='p341':
				print 'P.341'
			elif opts['bp-type']=='irs':
				print 'IRS (200-4000Hz)'
			elif opts['bp-type']=='mirs':
				print 'Modified IRS (200-5000Hz)'

			bn = os.path.basename (fileInRawCodec)
			inlist = tmpDir + '/' + bn+'-in-list.txt'
			outlist = tmpDir + '/' + bn + '-out-list.txt'
			os.system('echo ' + fileInRawCodec + ' > ' + inlist)
			os.system('echo ' + fileOutTmp4Raw + ' > ' + outlist)
			os.system(fantBin + ' -i ' + inlist + ' -o ' + outlist + ' -f ' + opts['bp-type'] + ' > /dev/null 2> ' + tmpDir + '/bp.log')
			if rmTmp:
				os.system('rm -f ' + inlist)
				os.system('rm -f ' + outlist)


	elif codec=='g711':
		print '  encoding G.711 (' + str(opts) + ')'
		os.system(g711bin + ' ' + opts['law'] + ' lilo ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding G.711 (' + str(opts) + ')'
		os.system(g711bin + ' ' + opts['law'] + ' loli ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='cvsd':
		print '  encoding CVSD (' + str(opts) + ')'
		os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileInRawCodec + ' -t cvu ' + fileOutTmp1Raw + ' rate ' + str(br2int(opts['bit-rate'])) + ' < /dev/null')
		print '  decoding CVSD (' + str(opts) + ')'
		os.system(soxBin+' -t cvu -r ' + str(br2int(opts['bit-rate'])) + ' ' + fileOutTmp1Raw + ' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileOutTmp4Raw + ' < /dev/null')

	elif codec=='g729a':
		print '  encoding G.729a'
		os.system(g729aEncBin + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding G.729a'
		os.system(g729aDecBin + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='g726':
		print '  encoding G.711+G.726 (' + str(opts) + ')'
		br=opts['bit-rate'][:-1]
		mode = int(br)/8
		os.system(g711bin + ' ' + opts['law'] + ' lilo ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		os.system(g726bin + ' ' + opts['law'] + ' load ' + str(mode) + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp2Raw + ' > /dev/null 2> enc2.log')
		print '  decoding G.711+G.726 (' + str(opts) + ')'
		os.system(g726bin + ' ' + opts['law'] + ' adlo ' + str(mode) + ' ' + fileOutTmp2Raw + ' ' + fileOutTmp3Raw + ' > /dev/null 2> dec1.log')
		os.system(g711bin + ' ' + opts['law'] + ' loli ' + fileOutTmp3Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> dec2.log')

	elif codec=='g722':
		if br2int(opts['bit-rate'])==64000:
			mode = 1
		elif br2int(opts['bit-rate'])==56000:
			mode = 2
		elif br2int(opts['bit-rate'])==48000:
			mode = 3
		else:
			print 'mode not supported'
			
		print '  encoding G.722 (' + str(opts) + ')'
		os.system(g722bin + ' -enc ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' ' + str(mode) + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding G.722 (' + str(opts) + ')'
		os.system(g722bin + ' -dec ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' ' + str(mode) + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='g728':

		print '  encoding G.728 (' + str(opts) + ')'
		os.system(g728bin + ' enc ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding G.728 (' + str(opts) + ')'
		if opts['lloss']>0:
			os.system(g728bin + ' -plcsize ' + str(opts['lloss']) + ' dec ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')
		else:
			os.system(g728bin + ' dec ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='c2':
		br=opts['bit-rate']
		if br=='3k2':
			opt='3200'
		elif br=='2k4':
			opt='2400'
		elif br=='1k4':
			opt='1400'
		elif br=='1k3':
			opt='1300'
		elif br=='1k2':
			opt='1200'
		else:
			print br + ' not supported'

		print '  encoding Codec2 (' + str(opts) + ')'
		os.system(c2EncBin + ' ' + opt + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding Codec2 (' + str(opts) + ')'
		os.system(c2DecBin + ' ' + opt + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')


	elif codec=='amr':
		br=opts['bit-rate']
		if opts['dtx']:
			opt='-dtx '
		else:
			opt=''
		if br=='4k75':
			opt=opt+'MR475'
		elif br=='5k9':
			opt=opt+'MR59'
		elif br=='6k7':
			opt=opt+'MR67'
		elif br=='7k4':
			opt=opt+'MR74'
		elif br=='7k95':
			opt=opt+'MR795'
		elif br=='10k2':
			opt=opt+'MR102'
		elif br=='12k2':
			opt=opt+'MR122'
		else:
			print br + ' not supported'

		print '  encoding AMR-NB ' + str(opts)
		os.system(amrNBEncBin + ' ' + opt + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding AMR-NB ' + str(opts)
		os.system(amrNBDecBin + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='amrwb':
		br=opts['bit-rate']
		if opts['dtx']:
			opt='-dtx '
		else:
			opt=''
		if br=='6k6':
			opt=opt+' 0 '
		elif br=='8k85':
			opt=opt+' 1 '
		elif br=='12k65':
			opt=opt+' 2 '
		elif br=='14k25':
			opt=opt+' 3 '
		elif br=='15k85':
			opt=opt+' 4 '
		elif br=='18k25':
			opt=opt+' 5 '
		elif br=='19k85':
			opt=opt+' 6 '
		elif br=='23k05':
			opt=opt+' 7 '
		elif br=='23k85':
			opt=opt+' 8 '
		else:
			print br + ' not supported'

		print '  encoding AMR-WB ' + str(opts)
		os.system(amrWBEncBin + ' ' + opt + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding AMR-WB ' + str(opts)
		os.system(amrWBDecBin + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='evrc':
		br=br2int(opts['bit-rate'])
		if opts['dtx']:
			optEnc='-W '+str(br)+' -D 1 -X Fsinp=8000'
			optDec='-W '+str(br)+' -D 1 -X Fsop=8000'
		else:
			optEnc='-W '+str(br)+' -D 0 -X Fsinp=8000'
			optDec='-W '+str(br)+' -D 0 -X Fsop=8000'

		print '  encoding EVRC-NB ' + str(opts)
		os.system(evrcBin + ' -i ' + fileInRawCodec + ' -o ' + fileOutTmp1Raw + ' -e ' + optEnc + '> /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding EVRC-NB ' + str(opts)
		os.system(evrcBin + ' -i ' + fileOutTmp1Raw + ' -o ' + fileOutTmp4Raw + ' -d ' + optDec + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='evrcwb':
		br=br2int(opts['bit-rate'])
		if opts['dtx']:
			opt='-W '+str(br)+' -D 1 -X Fsinp=16000 -X Fsop=16000'
		else:
			opt='-W '+str(br)+' -D 0 -X Fsinp=16000 -X Fsop=16000'

		print '  encoding EVRC-WB ' + str(opts)
		os.system(evrcBin + ' -i ' + fileInRawCodec + ' -o ' + fileOutTmp1Raw + ' -e ' + opt + '> /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding EVRC-WB ' + str(opts)
		os.system(evrcBin + ' -i ' + fileOutTmp1Raw + ' -o ' + fileOutTmp4Raw + ' -d ' + opt + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='gsmhr':
		if opts['dtx']:
			opt='dtx'
		else:
			opt='nodtx'

		print '  encoding GSM-HR ' + str(opts)
		print gsmHRBin + ' enc ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' ' + opt + ' > /dev/null 2> ' + tmpDir + '/enc.log'
		os.system(gsmHRBin + ' enc ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' ' + opt + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding GSM-HR ' + str(opts)
		os.system(gsmHRBin + ' dec ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' ' + opt + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='gsmefr':
		if opts['dtx']:
			opt='dtx'
		else:
			opt='nodtx'

		print '  encoding GSM-EFR ' + str(opts)
		os.system(gsmEFREncBin + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' ' + opt + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		os.system (gsmEFRCnvBin + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp2Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding GSM-EFR ' + str(opts)
		os.system(gsmEFRDecBin + ' ' + fileOutTmp2Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')

	elif codec=='gsmfr':

		print '  encoding GSM-FR '
		fileOutTmp1Gsm=re.sub('.raw','-'+str(stepNo)+'-tmp1-'+codec+'.gsm',fileInRaw) 
		os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileInRawCodec + ' ' + fileOutTmp1Gsm + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding GSM-FR '
		os.system(soxBin+' ' + fileOutTmp1Gsm + ' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		os.system('rm -f ' + fileOutTmp1Gsm)

	elif codec=='silk':
		if opts['dtx']:
			opt='-dtx'
		else:
			opt=''

		if int(opts['loss'])>0:
			optDec='-loss ' + opts['loss'] + ' -inbandfec'
		else:
			optDec=''

		print '  encoding SILK-NB ' + str(opts)
		os.system(silkBin + ' -e voip ' + str(fileInRate) + ' 1 ' + str(br2int(opts['bit-rate'])) + ' -bandwidth NB ' + opt + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding SILK-NB ' + str(opts)
		os.system(silkBin + ' -d ' + str(fileInRate) + ' 1 ' + optDec + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')

	elif codec=='silkwb':
		if opts['dtx']:
			opt='-dtx'
		else:
			opt=''

		if int(opts['loss'])>0:
			optDec='-loss ' + opts['loss'] + ' -inbandfec'
		else:
			optDec=''

		print '  encoding SILK-WB ' + str(opts)
		os.system(silkBin + ' -e voip ' + str(fileInRate) + ' 1 ' + str(br2int(opts['bit-rate'])) + ' -bandwidth WB ' + opt + ' ' + fileInRawCodec + ' ' + fileOutTmp1Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding SILK-WB ' + str(opts)
		os.system(silkBin + ' -d ' + str(fileInRate) + ' 1 ' + optDec + ' ' + fileOutTmp1Raw + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/enc.log')

	elif codec=='mp3':
		fileOutTmp1Mp3=re.sub('.raw','-'+str(stepNo)+'-tmp1-'+codec+'.mp3',fileInRaw)
		print '  encoding MP3 ' + str(opts)
		os.system(ffmpegBin + ' -f s16le -ar ' + str(fileInRate) + ' -i ' + fileInRawCodec + ' -strict experimental -y -acodec mp3 -ar ' + str(fileInRate) + ' -b:a ' + str(br2int(opts['bit-rate'])) + ' ' + fileOutTmp1Mp3 + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding MP3 ' + str(opts)
		os.system(ffmpegBin + ' -i ' + fileOutTmp1Mp3 + ' -y -f s16le -ar ' + str(fileInRate) + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')
		os.system('rm -f ' + fileOutTmp1Mp3)

	elif codec=='aac':
		fileOutTmp1Aac=re.sub('.raw','-'+str(stepNo)+'-tmp1-'+codec+'.aac',fileInRaw)
		print '  encoding AAC ' + str(opts)
		os.system(ffmpegBin + ' -f s16le -ar ' + str(fileInRate) + ' -i ' + fileInRawCodec + ' -strict experimental -y -acodec aac -ar ' + str(fileInRate) + ' -b:a ' + str(br2int(opts['bit-rate'])) + ' ' + fileOutTmp1Aac + ' > /dev/null 2> ' + tmpDir + '/enc.log')
		print '  decoding AAC ' + str(opts)
		os.system(ffmpegBin + ' -i ' + fileOutTmp1Aac + ' -strict experimental -y -f s16le -ar ' + str(fileInRate) + ' ' + fileOutTmp4Raw + ' > /dev/null 2> ' + tmpDir + '/dec.log')
		os.system('rm -f ' + fileOutTmp1Aac)

	else:
		print codec + ' not supported'
		exit()

	os.system('cp ' + fileOutTmp4Raw + ' ' + fileOutRaw)
	if rmTmp:
		if fileInRaw != fileInRawIni:
			os.system('rm -f ' + fileInRaw)
		os.system('rm -f ' + fileInRawCodec)
		os.system('rm -f ' + fileOutTmp1Raw)
		os.system('rm -f ' + fileOutTmp2Raw)
		os.system('rm -f ' + fileOutTmp3Raw)
		os.system('rm -f ' + fileOutTmp4Raw)
		if fileInRaw != fileInRawIni:
			os.system('rm -f ' + fileInRaw)
	fileInRaw=fileOutRaw
		
if options.samplerate=='auto':
	options.samplerate = fileInRate

fileName, fileExtension = os.path.splitext(outputFile)
outext = fileExtension[1:]


# convert from raw to wav again
if options.samplerate != fileInRate:
	print '\nresampling to ' + str(int(options.samplerate)/1000) + 'ksps'
	os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileInRaw + ' -t ' + outext + ' -r ' + str(options.samplerate) + ' ' + outputFile + ' < /dev/null')
else:
	print '\nwriting ' + str(int(options.samplerate)/1000) + 'ksps output'
	os.system(soxBin+' -t raw -e signed-integer -b 16 -r ' + str(fileInRate) + ' ' + fileInRaw + ' -t ' + outext + ' -r ' + str(options.samplerate) + ' ' + outputFile + ' < /dev/null')
if rmTmp:
	if len(fileOutRaw)>0:
		os.system('rm -f ' + fileOutRaw)
	os.system('rm -f ' + fileInRawIni)
	os.system('rm -f *.log')
	os.system('rm -rf ' + tmpDir)
