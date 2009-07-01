#!/usr/bin/env python
# features.py
import yaml, os
allfeatures = None
def features():
	global allfeatures
	if allfeatures: return allfeatures;
	allfeatures = yaml.load( open( os.path.join( os.path.dirname( __file__ ), "features.yaml" ) ) )
	return allfeatures

