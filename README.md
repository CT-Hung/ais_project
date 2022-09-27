# AIS project 

## Quick note
1. Python version: python3.10 up is fine
2. This code is only for the ais receiver connecting to the computer through COM port. 
3. Check the COM port number after the connection.
4. Change the COM port number at line 91 in AIS_receive.py
5. AIS_receive.py will save the ais data into the csv file at the path you choose.

## Install python package

    $ pip install pyserial pyais pandas

## Run code

    $ python AIS_receive.py