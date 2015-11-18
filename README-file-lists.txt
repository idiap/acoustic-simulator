======================
  CLEAN SPEECH FILES
======================

For reproducible evaluation of speaker recognition systems, we provide a list
of clean files chosen from the NIST SRE 2010 data set. This data set:

  - 16ksps PCM format
  - 3-to-15 minute long interviews
  - Clean recordings using lavalier microphones
	- 361 speakers for each of the train and test sets
  - Each train file has at least one test case

- train.list is a list of enrollment files, speaker ids and genders (m: male, f:
female)

- test.list is a list of test cases (2nd column), their speaker ids (1st column)
  and gender (3rd column)

Note that filenames have a letter 'A' appended to them, indicating only the
first audio channel needs to be extracted from the files.

From these lists, you should prepare the corresponding lists of train and test files with
absolute pathnames, i.e. pointing to the NIST SRE2010 audio files in your
system. These file lists will be degraded under diverse acoustic conditions using 
the provided simulator.

=========================================
  DEVELOPMENT, TRAIN AND TEST DATA SETS
=========================================
This package targets both the evaluation and development of robust speaker
recognition systems. System development can be sensitive to the acoustic 
conditions included in the development set, that are also present in the 
train and test sets. We address this issue in two ways:

  - A large noise (~2000 files, 80h), impulse response (~120 device and space
    impulse responses) and codec (~12 speech and audio codecs) database. The
    rationale here is to be able to reproduce a very large number of
    combined degradation processes to promote good generalization of machine 
		learning algorithms.

  - Split noise data into dev, train and test sets, to prevent overfitting
    of noise data. Still, we consider codecs and impulse responses as 
    processes rather than data and, given the small number of them, we decided 
    them to be shared across dev, train and test data sets.

To build the degradation dev, train and test sets we first assign train noise
files (361), then test files (644), keeping the rest for the development set
(1016). To do so just run:

  ./split-dev-train-test.py noise-file-list.txt train.list test.list

This will generate three files:

  noise-file-list-trn.txt
  noise-file-list-tst.txt
  noise-file-list-dev.txt

These noise file lists will be used when degrading a list of clean speech
files using the command 

  ./degrade-audio-list-safe-random.py \
    -N noise-file-list-XXX.txt \
    -D ir-device-file-list.txt \
    -P ir-space-file-list.txt 
    condition \
    file-list.txt \
    output-dir-XXX

	XXX: either 'trn','tst' or 'dev'
  condition:
[landline|cellular|satellite|voip|playback|interview].[|noisy08|noisy15]
	file-list.txt: list of clean files to degrade (with absolute path)
  output-dir-XXX: output directory for the degraded audio files

Note that 'safe-random' in the script name refers to reproducible random number generation across
machines. This is simply implemented as a list of pregenerated integer random
numbers in the file random. Please do not change the file 'random'.
