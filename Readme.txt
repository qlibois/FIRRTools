Python routines to analyze FIRR raw data

Data acquired by the Far InfraRed Radiometer come in .raw format. They are gathered in sequences, each stored in a directory. Each sequence directory contains a series of .raw files, along with a Temperature.txt file and a Header.txt file.

The tools provided here allow to analyze individual raw files, whole sequences and series of sequences (e.g. measurement flight or laboratory experiment)

Raw files, sequences and flights are built using Python objects (Class) on which various operations can be performed.