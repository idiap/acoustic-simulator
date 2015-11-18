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


import freesound
import string
import shutil
import unicodedata
import time
import glob
import os,sys,subprocess
import re

# paste your Freesound API v2 key below
# you can apply for one on http://www.freesound.org/apiv2/apply
apiKey=""




downloadAudio = True
delim=",.?-_:;'\"\' ()[]{}&^%$#@!~`<>|/"

def shortstr (s, ds, l=0):
	for d in ds:
		s = s.replace (d,'').lower()

	if l==0 :
		return s
	else:
		return s[0:l-1]

def remove_accents(input_str):
  nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
  return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def flatten(x):
	result = []
	for el in x:
		if hasattr(el, "__iter__") and not isinstance(el, basestring):
			result.extend(flatten(el))
		else:
			result.append(el)
	return result





if len(sys.argv)!=2:
	print "Syntax: download-noise-audio.py noise-db.txt"
	sys.exit (0)
else:
	soundList = sys.argv[1]

outDir = 'noise-samples'

try:
	os.stat(outDir)
except:
	os.mkdir(outDir)

c = freesound.FreesoundClient()
c.set_token(apiKey,"oauth2")

fileNo = 0;

f = open (soundList, 'r')
fnl = open ('noise-file-list.txt', 'a')
fntl = open ('noise-type-list.txt', 'a')

if downloadAudio:
	fout = open (outDir + '/' + 'noise-db.txt', 'a')

	with open(outDir + '/' + 'noise-db-fields.txt','a') as fr:
		fr.write ('noise-type sound-id username name duration src-audio-quality tgt-audio-quality tags\n') 

noisetypes=[]
for line in f.readlines():
	line = line.strip()
	s = line.split(' ')
	soundid =s[0]
	soundtag = s[1]
	soundlic = s[2]

	# check if sound is already downloaded
	g=glob.glob(outDir +'/' + soundtag + '/' + soundid + '*.wav')
	if len(g)>0:
		print 'skipping file ' + g[0]
		continue

	if soundtag not in noisetypes:
		noisetypes.append(soundtag)
		fntl.write(soundtag+'\n')
		fntl.flush()

	try:
		s = c.get_sound(soundid)
	except freesound.FreesoundException as e:
		if e.code == 400:
			continue
		if e.code == 429:
			print 'maximum limit of requests to freesound reached (2000/day)'
			exit()

	# get sound metadata
	# sound description until carrier return
	idxcr = s.description.find(u'\n')
	if idxcr>=0:
		s.description = s.description[0:idxcr-1]

	# duration
	sdur = "%.0f" % s.duration
	ssrate = "%.1f" % (s.samplerate / 1000)
	sbrate = "%.1f" % (s.bitrate / 1000)

	# short name
	sname = remove_accents(s.name.lower())
	sname = sname.replace(".wav",'')
	sname = sname.replace(".mp3",'')
	sname = sname.replace(".aiff",'')
	sname = shortstr (sname, delim, 20)
	sname = filter(lambda x: x in string.printable, sname)
	suname = shortstr (remove_accents(s.username.lower()), delim)
	suname = filter(lambda x: x in string.printable, suname)

	# file names
	ogg = str(s.id) + '-' + suname + '-' + sname + '-' + sdur + '.ogg'
	wavTmp = str(s.id) + '-' + suname + '-' + sname + '-' + sdur + '-tmp.wav'
	wav = str(s.id) + '-' + suname + '-' + sname + '-' + sdur + '.wav'

	if downloadAudio:
		outDirFile = outDir + '/' + soundtag
		try:
			os.stat(outDirFile)
		except:
			os.mkdir(outDirFile)

		print 'downloading sound ' + soundid + ', noise type ' + soundtag + ', ' + sdur + ' s'
		

#		s.retrieve_preview_lq_mp3(outDirFile, ogg)
#		s.retrieve_preview_hq_mp3(outDirFile, ogg)
#		s.retrieve_preview_lq_ogg(outDirFile, ogg)
		s.retrieve_preview_hq_ogg(outDirFile, ogg)


		if os.path.isfile(outDirFile + '/' + ogg):
			# get info about original file
			strSrcFileInfo=s.type+'-'+ssrate+'kHz'
			if s.type !='wav':
				#it is compressed => get bitrate
				strSrcFileInfo=strOriginalFileInfo+'-'+sbrate+'bps'
			if s.type == 'wav':
	 			print ' (' + s.type + ', ' + ssrate + 'ksps)'
			else:
	 			print ' (' + s.type + ', ' + ssrate + 'ksps, ' + sbrate + 'kbps)'

			# get info about output file
			o=subprocess.check_output('file ' + outDirFile + '/' + ogg, shell=True)
			o=o.split('\n')
			ln=o[0]
			sps=''
			m=re.search(r',\s+([0-9]+) Hz',ln)
			if m:
				sps=m.group(1)
			bps=''
			m=re.search(r',\s+[~]*([0-9]+) bps',ln)
			if m:
				bps=m.group(1)
			strTgtFileInfo='ogg-'+sps+'Hz-'+bps+'bps'

			if sps!='':
				fsps = float(sps)/1000
				ssps = '%.1f' % fsps
			else:
				ssps = '-'
			if bps!='':
				fbps = float(bps)/1000
				sbps = '%.1f' % fbps
			else:
				sbps = '-'
 			print '  to ' + outDirFile + '/' + ogg + ' (ogg, ' + ssps + 'ksps, ' + sbps + 'kbps)'

			# convert to PCM wav
			cmd = 'ffmpeg -i ' + outDirFile + '/' + ogg + ' -ar 16000 -ac 1 -y ' + outDirFile + '/' + wav + ' < /dev/null 2> /dev/null'
			os.system(cmd)
 			print '  converting to ' + outDirFile + '/' + wav + ' (wav, 16-bit PCM, 16ksps)'
			if os.path.isfile(outDirFile + '/' + wavTmp):
				os.remove(outDirFile + '/' + wavTmp)

		if os.path.isfile(outDirFile + '/' + wav):


			fout.write(soundtag + ' ' + str(s.id) + ' ' + suname + ' ' + sname + ' ' + sdur + ' ' + strSrcFileInfo + ' ' + strTgtFileInfo + ' ' + ','.join(s.tags) + '\n')
			fout.flush()

			fnl.write(outDirFile + '/' + wav + '\n')
			fnl.flush()
			os.fsync(fout.fileno())

		fileNo = fileNo + 1

	if not downloadAudio:
		time.sleep(2)
		
f.close()
fnl.close()
fntl.close()

if downloadAudio:
	fout.close()
