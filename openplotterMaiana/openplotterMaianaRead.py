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

import os, socket, time, ssl, json, datetime, sys
from openplotterSettings import conf
from openplotterSettings import platform
from openplotterSettings import language
from websocket import create_connection
from openplotterSignalkInstaller import connections

def main():
	if sys.argv[1] != '1':
		platform2 = platform.Platform()
		conf2 = conf.Conf()
		currentdir = os.path.dirname(os.path.abspath(__file__))
		currentLanguage = conf2.get('GENERAL', 'lang')
		package = 'openplotter-maiana'
		language.Language(currentdir, package, currentLanguage)
		skConnections = connections.Connections('MAIANA')
		token = skConnections.token
		if conf2.get('GENERAL', 'debug') == 'yes': debug = True
		else: debug = False
		if token:
			ws = False
			sock = False
			while True:
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					server_address = ('localhost', 10110)
					sock.connect(server_address)
					sock.setblocking(0)

					uri = platform2.ws+'localhost:'+platform2.skPort+'/signalk/v1/stream?subscribe=none'
					headers = {'Authorization': 'Bearer '+token}
					ws = create_connection(uri, header=headers, sslopt={"cert_reqs": ssl.CERT_NONE})

					tick = time.perf_counter()
					while True:
						time.sleep(0.01)
						if (time.perf_counter() - tick) > 3: raise Exception('')
						data = False
						try: data = sock.recv(1024)
						except: pass
						if data:
							tick = time.perf_counter()
							data = data.decode("utf-8")
							if '$PAI' in data:
								data = data.splitlines()
								for data2 in data:
									SKdata = {}
									data3 = data2.split('*')
									data3 = data3[0].split(',')
									#$PAINF,A,0x20*5B
									if data3[0] == '$PAINF':
										try: 
											noiseValue = int(data3[2],16)
											SKdata.update({"MAIANA.channel"+data3[1]+".noiseFloor":noiseValue})
											if conf2.get('MAIANA', 'noiseDetect') == '1':
												if noiseValue > 64:
													now = datetime.datetime.utcnow()
													now = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
													SKdata.update({"notifications.MAIANA.channel"+data3[1]+".noiseFloor":{"message":_("There may be electromagnetic interference near the MAIANA AIS antenna"),"state":"alert","method": ["visual"]}})
												else:
													SKdata.update({"notifications.MAIANA.channel"+data3[1]+".noiseFloor":None})
										except: pass
									#$PAITX,A,18*1C
									elif data3[0] == '$PAITX': 
										SKdata.update({"MAIANA.channel"+data3[1]+".transmittedMessageType":data3[2]})
									keys = []
									for i in SKdata:
										keys.append({"path":i,"value":SKdata[i]})
									if keys:     
										SignalK = {"updates":[{"$source":"OpenPlotter.maiana","values":keys}]}
										SignalK = json.dumps(SignalK) 
										ws.send(SignalK+'\r\n')
				except Exception as e: 
					if debug: 
						print(str(e))
						sys.stdout.flush()
					if ws: ws.close()
					if sock: sock.close()
					time.sleep(5)

	

if __name__ == '__main__':
	main()