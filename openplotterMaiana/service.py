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

import sys, subprocess

#TODO remove

if sys.argv[1]=='openplotter-maiana-read':
	if sys.argv[2]=='start':
		subprocess.call(['systemctl', 'enable', 'openplotter-maiana-read'])
		subprocess.call(['systemctl', 'start', 'openplotter-maiana-read'])
	if sys.argv[2]=='stop':
		subprocess.call(['systemctl', 'disable', 'openplotter-maiana-read'])
		subprocess.call(['systemctl', 'stop', 'openplotter-maiana-read'])
	if sys.argv[2]=='restart':
		subprocess.call(['systemctl', 'enable', 'openplotter-maiana-read'])
		subprocess.call(['systemctl', 'restart', 'openplotter-maiana-read'])