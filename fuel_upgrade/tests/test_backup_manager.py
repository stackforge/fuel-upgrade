# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from fuel_upgrade import config
from fuel_upgrade.engines.backup import BackupManager
from fuel_upgrade.tests.base import BaseTestCase


class TestBackupManager(BaseTestCase):

    def setUp(self):
        self.test_config = mock.Mock()

        self.supervisor_patcher = mock.patch(
            'fuel_upgrade.engines.backup.SupervisorClient')
        self.supervisor_class = self.supervisor_patcher.start()
        self.mock_supervisor = mock.MagicMock()
        self.supervisor_class.return_value = self.mock_supervisor

    def tearDown(self):
        self.supervisor_patcher.stop()

    def _build_config(self):
        self.test_config = config.build_config(None, None)

    @mock.patch("fuel_upgrade.config.get_version_from_config",
                return_value='0')
    @mock.patch("fuel_upgrade.config.read_yaml_config",
                return_value={
                    'ADMIN_NETWORK': {
                        'ipaddress': '0.0.0.0'
                    },
                    'postgres': {
                        'nailgun_dbname': 'nailgun',
                        'nailgun_user': 'nailgun',
                        'nailgun_password': 'nailgun',
                        'keystone_dbname': 'keystone',
                        'keystone_user': 'keystone',
                        'keystone_password': 'keystone'
                    }
                })
    def test_build_config(self, mock_read_yaml_config,
                          mock_get_version_from_config):
        self._build_config()

        mock_get_version_from_config.assert_called_once_with(
            '/etc/fuel/version.yaml')
        mock_read_yaml_config.assert_called_once_with(
            '/etc/fuel/astute.yaml')

    @mock.patch("shotgun.config.Config")
    @mock.patch("shotgun.manager.Manager")
    def test_upgrade(self, mock_shotgun_manager_class,
                     mock_shotgun_config_class):
        mock_shotgun_config = mock_shotgun_config_class.return_value
        mock_shotgun_manager = mock_shotgun_manager_class.return_value

        upgrader = BackupManager(self.test_config)
        upgrader.upgrade()

        self.mock_supervisor.start.assume_called_once_with('nailgun')
        mock_shotgun_config_class.assume_called_once_with(
            self.test_config.backup_config)
        mock_shotgun_manager_class.assume_called_once_with(
            mock_shotgun_config)
        mock_shotgun_manager.snapshot.assume_called_once()
