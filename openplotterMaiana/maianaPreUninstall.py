#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-maiana>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import os, subprocess, ujson
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	package = 'openplotter-maiana'
	language.Language(currentdir, package, currentLanguage)
	platform2 = platform.Platform()

	print(_('Removing connection to Signal K server for MAIANA commands...'))
	try:
		data = {}
		try:
			setting_file = platform2.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except Exception as e: print(str(e))
		if 'pipedProviders' in data:
			for idx, i in enumerate(data['pipedProviders']):
				if i['id'] == "maianaCommand": 
					data['pipedProviders'].pop(idx)
					data2 = ujson.dumps(data, indent=4, sort_keys=True)
					file = open(setting_file, 'w')
					file.write(data2)
					file.close()
					subprocess.call(['systemctl', 'stop', 'signalk.service'])
					subprocess.call(['systemctl', 'stop', 'signalk.socket'])
					subprocess.call(['systemctl', 'start', 'signalk.socket'])
					subprocess.call(['systemctl', 'start', 'signalk.service'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Removing services...'))
	try:
		subprocess.call(['systemctl', 'disable', 'openplotter-maiana-read'])
		subprocess.call(['systemctl', 'stop', 'openplotter-maiana-read'])
		subprocess.call(['rm', '-f', '/etc/systemd/system/openplotter-maiana-read.service'])
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Removing version...'))
	try:
		conf2.set('APPS', 'maiana', '')
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()