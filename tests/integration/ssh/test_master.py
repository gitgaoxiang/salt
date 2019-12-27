# -*- coding: utf-8 -*-
'''
Simple Smoke Tests for Connected SSH minions
'''

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Salt Testing libs
from tests.support.case import SSHCase
from tests.support.helpers import skip_if_not_root


class SSHMasterTestCase(SSHCase):
    '''
    Test ssh master functionality
    '''
    def test_can_it_ping(self):
        '''
        Ensure the proxy can ping
        '''
        ret = self.run_function('test.ping', minion_tgt='localhost')
        self.assertEqual(ret, True)

    @skip_if_not_root
    def test_service(self):
        service = 'cron'
        os_family = self.run_function('grains.get', ['os_family'], minion_tgt='localhost')
        os_release = self.run_function('grains.get', ['osrelease'], minion_tgt='localhost')
        if os_family == 'RedHat':
            service = 'crond'
        elif os_family == 'Arch':
            service = 'sshd'
        elif os_family == 'MacOS':
            service = 'org.ntp.ntpd'
            if int(os_release.split('.')[1]) >= 13:
                service = 'com.apple.AirPlayXPCHelper'
        ret = self.run_function('service.get_all', minion_tgt='localhost')
        self.assertIn(service, ret)
        self.run_function('service.stop', [service], minion_tgt='localhost')
        ret = self.run_function('service.status', [service], minion_tgt='localhost')
        self.assertFalse(ret)
        self.run_function('service.start', [service], minion_tgt='localhost')
        ret = self.run_function('service.status', [service], minion_tgt='localhost')
        self.assertTrue(ret)

    def test_grains_items(self):
        os_family = self.run_function('grains.get', ['os_family'], minion_tgt='localhost')
        ret = self.run_function('grains.items', minion_tgt='localhost')
        if os_family == 'MacOS':
            self.assertEqual(ret['kernel'], 'Darwin')
        else:
            self.assertEqual(ret['kernel'], 'Linux')

    def test_state_apply(self):
        ret = self.run_function('state.apply', ['core'], minion_tgt='localhost')
        for key, value in ret.items():
            self.assertTrue(value['result'])

    def test_state_highstate(self):
        ret = self.run_function('state.highstate', minion_tgt='localhost')
        for key, value in ret.items():
            self.assertTrue(value['result'])
