Create and go to source directory

  mkdir src
  cd src

1. Download ITU Software Tools (STL2009)

  - Open a web browser and download/save this file (accept the untrusted certificate if asked)

      https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-G.191-201003-I!!SOFT-ZST-E&type=items

  - Decompress the downloaded file T-REC-G.191-201003-I!!SOFT-ZST-E.zip

      unzip ~/Downloads/T-REC-G.191-201003-I\!\!SOFT-ZST-E.zip
 
    This is going to create the Software/stl2009 directory.

  - Compilation

    - G.722 (sub-band ADPCM, VoIP)

      cd Software/stl2009/g722
			make -f makefile.unx

    - G.728 (low-delay CELP, videoconferencing)

      cd ../g728/g728fixed
      make -f makefile.unx

    - G.726 (mu/A-law + ADPCM)

      cd ../../g726
      make -f makefile.unx

    - G.711 (mu/A-law)

      cd ../g711
      make -f makefile.unx

    - Go back to src root dir

      cd ../../../

2. Download G.729 (low-delay CS-ACELP, satellite)

  - Open a web browser and download this file (accept the untrusted
	  certificate if asked)

    http://www.itu.int/rec/T-REC-G.729-201206-I/en

  - Decompress the downloaded file T-REC-G.729-201206-I\!\!SOFT-ZST-E.zip

    unzip ~/Downloads/T-REC-G.729-201206-I\!\!SOFT-ZST-E.zip

    This is going to create the Software/G729_Release3 directory

  - Compilation

    cd Software/G729_Release3/g729AnnexA/c_code

    - Rename all files to lowercase

      for i in `ls` ; do mv -f "$i" `echo "$i" | tr A-Z a-z` ; done

    - Create Makefile and make both coder and decoder

			make -f coder.mak
			make -f decoder.mak

    - Go back to src root dir

      cd ../../../../

3. Filter and Add Noise tool (FaNT)

  - Download the package

    wget http://dnt.kr.hsnr.de/aurora/download/fant.tar.gz

  - Make dir, decompress and compile

    mkdir fant
    cd fant
    tar xzvf ../fant.tar.gz
    make -f filter_add_noise.make

  - Go back to src root dir

    cd ../

4. OPUS library (silk codec used by Skype)

  - Download the package

    wget http://downloads.xiph.org/releases/opus/opus-1.1.tar.gz

  - Compile

	  tar xzvf opus-1.1.tar.gz
    cd opus-1.1
    make -f Makefile.unix

  - Go back to src root dir

    cd ../

5. SOX (version 14.4.2, older versions might fail in some operations)

  - Download SOX package

    http://sourceforge.net/projects/sox/

    Click Download green button and wait for some seconds

  - Decompress the downloaded file sox-14.4.2.tar.bz2

    tar -xvjf ~/Downloads/sox-14.4.2.tar.bz2

	- Compilation

    cd sox-14.4.2
    ./configure --enable-static --disable-shared
    make

  - Go back to src root dir

    cd ../

6. FFMPEG (with MP3 and AAC support)

  - Download MMPEG package

    http://www.ffmpeg.org/download.html

    Click on green button.

  - Decompress the downloaded file ffmpeg-2.6.2.tar.bz2

    tar -xvjf ~/Downloads/ffmpeg-2.6.2.tar.bz2

  - Download LAME library for FFMPEG MP3 support

    http://sourceforge.net/projects/lame/files/lame/3.99/

    click on file lame-3.99.5.tar.gz and wait for a few seconds

  - Compile LAME library

    tar xzvf ~/Downloads/lame-3.99.5.tar.gz
    cd lame-3.99.5
    ./configure
    make
		sudo make install
    cd ../

  - Download aacplus library for FFMPEG AAC support
 
    wget http://tipok.org.ua/downloads/media/aacplus/libaacplus/libaacplus-2.0.2.tar.gz 
      
  - Compile AAC library

		sudo apt-get install libtool
    tar xzvf libaacplus-2.0.2.tar.gz
    cd libaacplus-2.0.2
    ./autogen.sh --enable-shared --enable-static
    make
    sudo make install
    cd ../

  - Compile FFMPEG

    cd ffmpeg-2.6.2
    ./configure --enable-gpl --enable-libmp3lame --enable-nonfree --enable-libaacplus --disable-yasm
    make
    sudo make install
    cd ../

7. AMR-NB

  - Download AMR-NB package

    wget http://www.etsi.org/deliver/etsi_ts/126000_126099/126073/03.03.00_60/ts_126073v030300p0.zip

  - Decompress AMR-NB

    mkdir amr-nb
    cd amr-nb
    unzip ../ts_126073v030300p0.zip

  - Compile

    Change architecture. Add lines

        #define linux 1
        #define i386 1

    at the top of file typedefs.h .

	  make -f makefile


  - Go back to src root dir

		cd ../

8. AMR-WB

  - Download AMR-WB package from

    http://www.itu.int/rec/T-REC-G.722.2-200811-I!AnnC

  - Decompress codec

    unzip ~/Downloads/T-REC-G.722.2-200811-I\!AnnC\!SOFT-ZST-E.zip
    cd G722-2AnxC-v.7.1.0/c-code-v.7.1.0

    Change architecture. Add lines

        #define linux 1
        #define i386 1

    at the top of file typedefs.h.

    make -f makefile.gcc

    cd ../../

8. Convert SPHERE files to wav

  - Download sph2pipe

    wget https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/ctools/sph2pipe_v2.5.tar.gz

  - Compile code

    tar xzvf sph2pipe_v2.5.tar.gz
    cd sph2pipe_v2.5
    gcc -o sph2pipe shorten_x.c file_headers.c sph2pipe.c -lm

    cd ../

9. Qualcomm-ICSI-OGI noise reduction

  - Download

    wget http://www.icsi.berkeley.edu/Speech/papers/qio/qio.zip

  - Decompress

    unzip qio.zip
		cd aurora-front-end/qio/src
		make

		cd ../../../

10. Codec2 (very low bit-rate coding)

  - Download

    svn co https://svn.code.sf.net/p/freetel/code/codec2 codec2
		cd codec2
    mkdir build_linux
    cd build_linux
    cmake ../
    make
    cd ../../
