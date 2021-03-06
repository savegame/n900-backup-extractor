#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
Extracts vcard data from the addressbook database (addressbook.db) and
writes it as separate vcards to a folder (./vcards).
"""

import sys
import os
import vobject
from bsddb3 import db
import slugify

import utils

if len(sys.argv) != 2:
  utils.show_usage('%s [path to addressbook.db]' % sys.argv[0])

fileName = sys.argv[1].strip()
vcardsDir = 'vcards'

addressBookDb = db.DB()
try:
  # Create the vcards directory (if needed)
  if not os.path.exists(vcardsDir):
    os.makedirs(vcardsDir)

  # Try to open addressbook database
  addressBookDb.open(fileName, None, db.DB_HASH, db.DB_DIRTY_READ)

  cursor = addressBookDb.cursor()
  record = cursor.first()

  # Fill a list with vcard strings from db
  vCards = []
  while record:

    # Get vcard string and correct line endings
    vCardString = record[1].replace('\x00', '\r\n')
    vCards.append(vCardString)

    record = cursor.next()

  # Write vcard strings
  for vCard in vCards:

    try:
      parsedVCard = vobject.readOne(vCard)
    except Exception as err:
      print >> sys.stderr, "Failed to parse vCard data: %s\nvCard data:\n%s" % (err, vCard)
      continue

    # Not all entries have a n(ame) attribute
    if hasattr(parsedVCard, 'n'):
      vCardName = slugify.slugify(unicode(parsedVCard.n.value))
      # Construct file name
      vCardName = '%s/%s.vcf' % (vcardsDir, vCardName)

      # Open vcard for writing
      with open(vCardName, 'w') as fd:
        fd.write(vCard)
      fd.close()

except OSError, err:
  utils.show_error('Could not create \'%s\' folder: %s' % (vcardsDir, err))
except db.DBError, err:
  utils.show_error('BerkeleyDB said: %s' % err)
except IOError, err:
  utils.show_error('Could not open csv file \'%s\' for writing: %s' % (vCardName, err))
