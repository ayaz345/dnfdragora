#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import errno, glob, polib, re, os, getopt, sys
from time import strftime

def usage():
    print('\nUsage: python %s [OPTION]' %os.path.basename(sys.argv[0]))
    print('       generate pot catalogs and updates po files for desktop resources in the specified directory')
    print('Options: -h, --help                              : usage')
    print('         -d <directory>, --directory <directory> : directory with desktop files')
    sys.exit(2)
try:
    opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help", "directory="])
except getopt.GetoptError:
    usage() # print help information and exit

directory='.'
for o,a in opts:
    if o in ("-h", "--help"):
        usage()
    if o in ("-d", "--directory"):
        directory=a

directory = directory.rstrip('/')

if (directory != '') and (os.path.isdir(directory) == False):
    sys.exit('Specified directory does not exist')

# Find all desktop files
files = []
for rootdir, dirnames, filenames in os.walk(directory):
    files.extend(glob.glob(f"{rootdir}/*.desktop"))

# Define Templates and po directory name
messagetemplate='(?<=\n)(Name=.*?\n|Comment=.*?\n|GenericName=.*?\n)'
mpattern=re.compile(messagetemplate,re.DOTALL)
translationtemplate='(?<=\n)(Name\[.*?\n|Comment\[.*?\n|GenericName\[.*?\n)'
tpattern=re.compile(translationtemplate,re.DOTALL)
podir = 'po/desktop'

# Write POT file
pot = polib.POFile('',check_for_duplicates=True)
potcreationtime = strftime('%Y-%m-%d %H:%M%z')
pot.metadata = {
  'Project-Id-Version': 'dnfdragora desktop files translation',
  'Report-Msgid-Bugs-To': 'i18n-discuss@ml.mageia.org',
  'POT-Creation-Date': potcreationtime,
  'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
  'Last-Translator': 'FULL NAME <EMAIL@ADDRESS>',
  'Language-Team': 'LANGUAGE <LL@li.org>',
  'MIME-Version': '1.0',
  'Content-Type': 'text/plain; charset=UTF-8',
  'Content-Transfer-Encoding': '8bit',
  }

for langfile in files:
  langfiledir = langfile.replace('.desktop', '')
  langfilename = langfiledir.rpartition('/')[2]
  # Create localization directories if needed
  try:
    os.makedirs(podir)
  except OSError as e:
    if e.errno != errno.EEXIST:
        raise
  #open desktop file
  text = open(langfile,"r").read()

  # Parse contents and add them to POT
  for mblock in mpattern.findall(text):
    mblock_stripped = mblock.strip('\n')
    message_comment, message_id = mblock.strip('\n').split('=')
    potentry = polib.POEntry(
      msgctxt = message_comment,
      msgid = message_id,
      msgstr = '',
      occurrences=[(langfile,'')]
      )
    if message_id != '':
      try:
        pot.append(potentry)
      except ValueError:
        print('The entry already exists')
pot.save('./po/desktop/dnfdragora_desktop.pot')

# Merge translations
for pofile in glob.glob(f'{podir}/*.po'):
    lang = pofile[:-3].rsplit('/',1)[1]
    pofilename = pofile
    po = polib.pofile(pofilename)
    po.merge(pot)
    po.save(pofilename)

for langfile in files:
    with open(langfile,"r") as deskfile:
        text = deskfile.read()
    with open(langfile,"w") as deskfile:
        for transblock in tpattern.findall(text):
          text = text.replace(transblock, '')

          # Parse PO files
        for pofile in sorted(glob.glob(f'{podir}/*.po'), reverse = True):
            lang = pofile[:-3].rsplit('/',1)[1]
            pofilename = pofile
            po = polib.pofile(pofilename)
            for entry in po.translated_entries():
              if entry.msgid in text:
                origmessage = '\n' + entry.msgctxt + '=' + entry.msgid + '\n'
                origandtranslated = '\n' + entry.msgctxt + '=' + entry.msgid + '\n' + entry.msgctxt + '[' + lang + ']=' + entry.msgstr + '\n'
                text = text.replace(origmessage, origandtranslated)

        deskfile.write(text)

