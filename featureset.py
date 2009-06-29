#!/usr/bin/env python
# featureset.py
# 

import yaml, random, uuid
from google.appengine.ext import db

allfeatures = None

class FeatureSet( db.Expando ):
	"""
		Defines the features for a given visitor.  Note that this Expando model 
		implementation contains no static fields.  All fields are dynamic, and
		are determined by those listed in features.yaml
	"""
	pass

def featureset( key=None, **kwargs ):
	"""
		Static factory method for creating or retrieving FeatureSet instances.
	"""
	
	# Lazy-load feature data
	global allfeatures
	allfeatures = allfeatures or yaml.load( open( "features.yaml" ) )
	
	# Check request and lookup existing feature set, or create new empty set
	key = key or "uuid:%s" % str( uuid.uuid4() )
	fs = db.get( db.Key.from_path( "FeatureSet", key ) ) or FeatureSet( key_name=key )
	changed = not fs.is_saved()
	
	# Fill in any keyword arguments
	for k, v in kwargs.iteritems():
		if hasattr( fs, k ) and getattr( fs, k ) == v: continue
		changed = True
		setattr( fs, k, v )		

	# Fill in FeatureSet instance from allfeatures
	for feature, groups in allfeatures.iteritems():
	
		# If groups is really just one value, the only choice is to set it
		if type(groups) != dict:
			if hasattr( fs, feature ) and getattr( fs, feature ) == groups: continue
			changed = True
			setattr( fs, feature, groups )
			continue
	
		# If the FeatureSet already has this feature, make sure it's a legal value
		if hasattr( fs, feature ):
			oldval = getattr( fs, feature )
			found = False
			for value, frequency in groups.iteritems():
				if oldval == value: 
					found = True
					break
			if found: continue
			
		# Randomly pick from the feature's groups based on defined frequencies
		stops = []
		last = 0
		for value, frequency in groups.iteritems():
			last += frequency
			stops.append( ( last, value ) )
		r = random.uniform( 0.0, last )
		for i in range( len( stops ) ):
			if r < stops[i][0]:
				break
		
		# Set the feature on the feature set
		changed = True
		setattr( fs, feature, stops[i][1] )
		
	# Save the FeatureSet
	if changed: fs.put()
	return fs

