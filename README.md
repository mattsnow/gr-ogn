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

1. Open the GRC flowchart found in the /examples directory.
2. Modify the File Source block to point to test_data.bin, which is also in the /examples directory.
3. Execute the flowgraph. The program will decode the OGN packet recorded in the sample data. 
4. The decoded output will be displayed in the GRC Reports Panel.
5. The decoded output will be logged to two log files that are located in the /build directory. 

The decoded positions can also be viewed in a Google Maps window. To do this, webserver.sh needs to be made executable. This can be set in the properties window. Then to start the web server, navigate a console window to the same directory and enter: 

./webserver.sh

Navigating to http://127.0.0.1:8000 will show the directory listing. The "ogn_json" log file needs to be copied from the /build directory into the same directory as ogn_map.html. Then simply load ogn_map.html to view the plotted positions.

<h3>Work on this repository is still ongoing and more documentation will be provided soon</h3>
