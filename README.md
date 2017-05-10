<h1>gr-ogn</h1>

Python framer and decoder blocks for processing OGN messages in GNU Radio. Includes example flow graph for end-to-end processing of messages.

<h1>Installation</h1>

The following instructions will take a clean install of Ubuntu 16.04.2 to a point where the example can be run. 

<h2>Prerequisites</h2>

sudo apt-get install gnuradio<br>
sudo apt-get install libusb-1.0-0-dev<br>
sudo apt install cmake<br>
sudo apt install git<br>

<h2>rtl-sdr</h2>

git clone git://git.osmocom.org/rtl-sdr.git<br>
cd rtl-sdr/<br>
mkdir build<br>
cd build<br>
cmake ../<br>
make<br>
sudo make install<br>
sudo ldconfig<br>

<h2>gr-osmosdr</h2>

sudo apt-get install gr-osmosdr

<h2>gr-ogn</h2>

git clone https://github.com/mattsnow/gr-ogn.git<br>
cd gr-ogn/<br>
mkdir build<br>
cd build<br>
cmake ../<br>
make<br>
sudo make install<br>
sudo ldconfig<br>

<h1>Usage</h1>

Modify GRC flowchart to point to correct recorded data
Logs will be created in home directory 
Can set script as executable 
Ensure JSON file is in same location as .html
Load up .html file

Load the flowgraph from the examples directory in GNU Radio Companion. It should work out of the box and provide decoded messages to the console and to two log files. 

By running the web server script (SimpleHTTPServer) you can open the provided web page, which will plot any received transmission. 

<h3>Work on this repository is still ongoing and more documentation will be provided soon</h3>
