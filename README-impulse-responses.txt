A collection of open-source impulse responses is available under
impulse-reponses-original directory. Due to license details, these are
provided in its original form. You can find a number of interesting device and
space impulse responses on Fokke van Saane's page

  http://fokkie.home.xs4all.nl/IR.htm

Due to licensing issues, we cannot redistribute them in this package, but here are
the commands to be run to install those that we use in this package:

  # install fokke van saane's device IR
  cd impulse-responses-original/devices
  mkdir fokkevansaane
  cd fokkevansaane
  wget http://fokkie.home.xs4all.nl/Files/Speakers%20and%20telephones.zip
  unzip Speakers\ and\ telephones.zip
  cd ../../../

  # install fokke van saane's space IR
  cd impulse-responses-original/spaces/medium
  mkdir fokkevansaane
  cd fokkevansaane
  wget http://fokkie.home.xs4all.nl/Files/Church%20Schellingwoude.zip
  unzip Church\ Schellingwoude.zip
	cd ../../large
	mkdir fokkevansaane
  cd fokkevansaane
	wget http://fokkie.home.xs4all.nl/Files/Factory%20Hall.zip
	unzip Factory\ Hall.zip
  cd ../../../../

It is only left to process the provided and downloaded IRs into the directory
impulse-responses. This involves, format conversion, 8ksps/16ksps resampling 
and normalization. It also normalizes directory and file names

You will need python installed and the following two packages

  scikits.audiolab
  scikits.samplerate

Then, just run

  ./prepare-impulse-responses.py

This is going to create a directory called 'impulse-responses' with the IRs
ready to be processed by the script degrade-audio-safe-random.py
