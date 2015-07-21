# DayOneCarousel
# By Jack Hughes
# 
# A script for finding [Day One](http://dayoneapp.com) entries that don't
# yet have a photo attached, but a photo was taken on the day of the entry 
# and could be attached to it. The script obtains photos from the Camera 
# Uploads folder used by Dropbox's [Carousel](https://carousel.dropbox.com).
#
# https://github.com/jackhughesweb/DayOneCarousel

import os
import plistlib
import exifread
from datetime import datetime
from datetime import timedelta
import getpass

# How long ago to search
years_ago = 1

# Set location of files
username = getpass.getuser()
journal_location = '/Users/' + username + '/Dropbox/Apps/Day One/Journal.dayone'
journal_entries_location = journal_location + '/entries'
journal_photos_location = journal_location + '/photos'
photos_location = '/Users/' + username + '/Dropbox/Camera Uploads'

# Arrays for data
journal_entries = []
photo_entries = []
date_entries = []
date_photos = []
entries_output_raw = []
entries_output = []

# Get date
days_ago = years_ago * 365
check_date = datetime.now() - timedelta(days=days_ago)

# Add all entries to an array
files_in_dir = os.listdir(journal_entries_location)
for file_in_dir in files_in_dir:
	journal_entries.append(os.path.splitext(file_in_dir)[0])
	# Check for Dropbox Conflicted Copies
	if "conflict" in file_in_dir:
		with open(journal_entries_location + '/' + file_in_dir, 'rb') as fp:
		    pl = plistlib.load(fp)
		print('Conflict found in entries file ' + file_in_dir + ' with date ' + pl['Creation Date'].strftime('%Y-%m-%d'))
		raise SystemExit
		
# Add all photos to an array
files_in_dir = os.listdir(journal_photos_location)
for file_in_dir in files_in_dir:
	photo_entries.append(os.path.splitext(file_in_dir)[0])
	# Check for Dropbox Conflicted Copies
	if 'conflict' in file_in_dir:
		print('Conflict found in photos file ' + file_in_dir)
		raise SystemExit

# Remove entries that already have a photo attached
for entry in journal_entries:
	for photo in photo_entries:
		if photo == entry:
			journal_entries.remove(entry)

# Get dates of entries within date period without photos
for entry in journal_entries:
	with open(journal_entries_location + '/' + entry + '.doentry', 'rb') as fp:
	    pl = plistlib.load(fp)
	    if check_date < pl['Creation Date']:
		    date_entries.append(pl['Creation Date'].strftime('%Y-%m-%d'))

# Sort dates
date_entries.sort()

# Get dates of pictures in Camera Uploads (may take a while, needs optimising)
files_in_dir = os.listdir(photos_location)
for file_in_dir in files_in_dir:
	with open(photos_location + '/' + file_in_dir, 'rb') as fp:
		tags = exifread.process_file(fp, stop_tag='EXIF DateTimeOriginal')
		if 'EXIF DateTimeOriginal' in tags:
			date_photos.append(datetime.strptime(tags['EXIF DateTimeOriginal'].printable[:10], '%Y:%m:%d').strftime('%Y-%m-%d'))

# Sort photo dates
date_photos.sort()

# Check if there is an photo for each entry in the time interval set without a photo
for date_entry in date_entries:
	for date_photo in date_photos:
		if date_entry == date_photo:
			entries_output_raw.append(date_entry)

# Sort dates of entries with possible photos
entries_output = sorted(list(set(entries_output_raw)))

# Output
print('Entries awaiting photos (within ' + str(years_ago) + ' year(s) from now):')
for entry in entries_output:
	print(entry)
