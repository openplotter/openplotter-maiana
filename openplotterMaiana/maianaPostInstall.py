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

import os, ujson, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	package = 'openplotter-maiana'
	language.Language(currentdir, package, currentLanguage)
	platform2 = platform.Platform()

	print(_('Adding connection to Signal K server for MAIANA commands...'))
	try:
		data = {}
		exists = False
		connection = {"pipeElements": [{"type": "providers/simple","options": {"logging": False,"type": "NMEA0183","subOptions": {"validateChecksum": False,"type": "udp","suppress0183event": True,"port": "40440","sentenceEvent": "maianaCommand"}}}],"id": "maianaCommand","enabled": True}
		try:
			setting_file = platform2.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except Exception as e: print(str(e))
		if 'pipedProviders' in data:
			for idx, i in enumerate(data['pipedProviders']):
				if i['id'] == "maianaCommand": 
					exists = True
					data['pipedProviders'][idx] = connection
			if not exists: data['pipedProviders'].append(connection)
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

	print(_('Creating services...'))
	try:
		fo = open('/etc/systemd/system/openplotter-maiana-read.service', "w")
		fo.write( '[Service]\nEnvironment=OPrescue=0\nEnvironmentFile=-/boot/firmware/config.txt\nExecStart=openplotter-maiana-read $OPrescue\nUser='+conf2.user+'\nRestart=always\nRestartSec=3\n\n[Install]\nWantedBy=local-fs.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))
	
	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'maiana', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()