#!/usr/bin/env python

from setuptools import setup
import os.path

def get_platform_file_list():
      data_files = []
      repo_path = os.path.abspath(os.path.dirname(__file__))
      data_path = os.path.join(repo_path, 'platform')
      platforms = os.listdir(data_path)
      for platform in platforms:
          data_files.append( (os.path.join('/usr/share/sonic', platform),
                             ['platform/' + platform + '/alias_map.json', 
                              'platform/' + platform + '/port_config.ini', 
                              'platform/' + platform + '/sensors.conf']  
                             ))
      return data_files

setup(name='sonic-config-engine',
      version='1.0',
      description='Utilities for generating SONiC configuration files',
      author='Taoyu Li',
      author_email='taoyl@microsoft.com',
      url='https://github.com/Azure/sonic-buildimage',
      py_modules=['minigraph'],
      scripts=['sonic-cfggen'],
      data_files=get_platform_file_list(),
      install_requires=['lxml', 'jinja2', 'netaddr', 'ipaddr', 'pyyaml'],
     )
