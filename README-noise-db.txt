The noise database consists of around 2000 noise files of 1 to 8 minutes long available online on the freesound.org website. The audio files are downloaded from the website via an API (freesound.py) and the whole process is automated by calling the script

  ./download-noise-db.py noise-db.txt

noise-db.txt is a file consisting of the 2000 file ids together with a
manually-tagged noise category and the license type. To run the script above
you need to obtain a valid API key from

  http://www.freesound.org/apiv2/apply

and replace the line

  apiKey=""

by

  apiKey="YOUR_API_KEY"

in line 13 of 'download-noise-db.py'

Please note that download is limited to 2000 requests per day and you might
need to run it twice to complete the 2021 noise files.

This command will generate

  - noise-file-list.txt : list of 16ksps down-sampled files downloaded from
    freesound.org
  - noise-samples: directory where noise files were downloaded
