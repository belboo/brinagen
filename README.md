# brinagen

A set of custom utilities for handling genetic data
from Illumina at certain stages of the analysis pipeline.

Mainly intended for use by Sabrina Träger, but may, perhaps,
be useful to someone else...

# Components

1. Python package "brinagen"
	contains several utilities for handling data

	Modules:
	- snp_dict: a simple DNA fragment dictionary
				to translate database IDs to shorter names.
				Stores the dictionary in JSON format.

		Functions:
		- snp_dict_load:	load dictionary from JSON file
		- snp_dict_list:	formats and prints the dictionary
		- snp_dict_lookup:	returns shorter names for IDs
		- snp_dict_ilookup:	reverse lookup
		- snp_dict_add:		adds new entries to the dictionary

	- tools: useful utilities
		Functions:
		- unique:			return unique elements of a list

2. Sample SNP dictionary
	located in ./testdata folder
	contains sample dicitonary snpdict.json
