#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2021 by Sailoog <https://github.com/openplotter/openplotter-maiana>
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

import socket, time, ssl, json
from openplotterSettings import conf
from openplotterSettings import platform
from websocket import create_connection

def main():
	platform2 = platform.Platform()
	conf2 = conf.Conf()
	token = conf2.get('MAIANA', 'token')
	device = conf2.get('MAIANA', 'device')
	if token and device:
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
						if '$PA' in data:
							data = data.splitlines()
							for data2 in data:
								SKdata = {}
								data3 = data2.split('*')
								data3 = data3[0].split(',')
								#$PAINF,A,0x20*5B
								if data3[0] == '$PAINF': 
									try: SKdata.update({"MAIANA.channel"+data3[1]+".noiseFloor":int(data3[2],16)})
									except: pass
								#$PAITX,A,18*1C
								elif data3[0] == '$PAITX': 
									SKdata.update({"MAIANA.channel"+data3[1]+".transmittedMessageType":data3[2]})
								#$PAISYS,11.0.0,3.1.0,00010*2E
								elif data3[0] == '$PAISYS': 
									try: SKdata.update({"MAIANA.hardwareRevision":data3[1],"MAIANA.firmwareRevision":data3[2],"MAIANA.serialNumber":data3[3],"MAIANA.MCUtype":data3[4]})
									except: SKdata.update({"MAIANA.hardwareRevision":data3[1],"MAIANA.firmwareRevision":data3[2],"MAIANA.serialNumber":data3[3],"MAIANA.MCUtype":''})
								#$PAISTN,987654321,NAUT,,37,0,0,0,0*2A
								elif data3[0] == '$PAISTN':
									try:
										SKdata.update({"MAIANA.station.MMSI":data3[1],"MAIANA.station.vesselName":data3[2],"MAIANA.station.callSign":data3[3],"MAIANA.station.vesselType":int(data3[4]),"MAIANA.station.LOA":int(data3[5]),"MAIANA.station.beam":int(data3[6]),"MAIANA.station.portOffset":int(data3[7]),"MAIANA.station.bowOffset":int(data3[8])})
									except: pass
								#$PAITXCFG,1,0,1,1,0*0
								elif data3[0] == '$PAITXCFG':
									try:
										SKdata.update({"MAIANA.transmission.hardwarePresent":int(data3[1]),"MAIANA.transmission.hardwareSwitch":int(data3[2]),"MAIANA.transmission.softwareSwitch":int(data3[3]),"MAIANA.transmission.stationData":int(data3[4]),"MAIANA.transmission.status":int(data3[5])})
									except: pass
								keys = []
								for i in SKdata:
									keys.append({"path":i,"value":SKdata[i]})
								if keys:     
									SignalK = {"updates":[{"$source":"OpenPlotter.maiana","values":keys}]}
									SignalK = json.dumps(SignalK) 
									ws.send(SignalK+'\r\n')
			except: 
				if ws: ws.close()
				if sock: sock.close()
				time.sleep(5)

	

if __name__ == '__main__':
	main()