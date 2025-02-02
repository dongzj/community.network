"""Operation for files in COM7 devices.
"""
from lxml import etree
from ncclient.xml_ import qualify
from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.namespaces import NCDATA, NCDATA_C, NCACTION
from ansible_collections.community.network.plugins.module_utils.network.pycw7.utils.xml.lib import *


class File(object):
    """This class is used to get data and configure a specific File.

    Args:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.

    Attributes:
        device (COM7): connected instance of a ``pycw7.comware.COM7``
            object.

    """
    def __init__(self, device, filename, comparefile=None):
        self.device = device
        if filename:
            self.filename = filename
        if comparefile:
            self.comparefile = comparefile
        self._diff_response = ''
        self._switch_response = []
        self._original__diffs = []
        self._diffs = []
        self._show_response = ''
        self._content = []

    def get_rollback_file_lists(self):
        """Get a list of rollback files list that exist on the switch.

        Returns:
            It returns a list of rollback files as strings.
        """
        E = data_element_maker()
        top = E.top(
            E.Configuration(
                E.Files(
                    E.File()
                )
            )
        )
        nc_get_reply = self.device.get(('subtree', top))
        file_names = findall_in_data('Name', nc_get_reply.data_ele)
        filenames = [file_name.text for file_name in file_names]
        return filenames

    def _get__diffs_between_fies(self):
        """Compare difference between two rollback files
        """
        cmds = 'display diff configfile {0} configfile {1}'.format(
            self.filename, self.comparefile)

        # raw string output taken directly from the switch showing the diff
        self._diff_response = self.device.cli_display(cmds)

    def compare_rollback_files(self):
        """Compare new config file to the existing current running config

        Returns:
            This returns a tuple of two elements that are both lists.

            The first element has a summary of diffs (self._diffs) and
            the second element is the exact output from the 'display diff'
            command, but as a list (self._original__diffs).
        """
        self._diffs = []
        file_cfg = []
        compare_cfg = []

        if not self._diff_response:
            self._get__diffs_between_fies()

        # same as _diff_response, but as a list with each line as an element
        self._original__diffs = self._diff_response.split('\n')

        for line in self._original__diffs:
            if line.strip().startswith('-') and '#' not in line:
                file_cfg.append(line.strip('-').strip())
            elif line.strip().startswith('+') and '#' not in line:
                compare_cfg.append(line.strip('+').strip())

        commands_to_apply = set(compare_cfg).difference(file_cfg)
        commands_to_remove = set(file_cfg).difference(compare_cfg)

        # diffs is summary of exactly which lines are changing in
        # _original__diffs because _diffs from switch show everything
        for each in commands_to_apply:
            self._diffs.append('+' + each)

        for each in commands_to_remove:
            self._diffs.append('-' + each)

        return self._diffs, self._original__diffs

    def _get__content_fie(self):
        """show the content for the rollbackfile
        """
        cmds = 'more {}'.format(self.filename)

        # raw string output taken directly from the switch showing the diff
        self._show_response = self.device.cli_display(cmds)

    def get_file_content(self):
        """show the config file content

        Returns:
            This returns a lists for the content.
            but as a list (self._content_file).
        """
        self._content = []

        if not self._show_response:
            self._get__content_fie()

        # same as _diff_response, but as a list with each line as an element
        self._content = self._show_response.split('\n')

        return self._content

    def build_startupfile(self, startup):
        E = action_element_maker()
        top = E.top(
            E.Configuration(
                E.Files(
                    E.File(
                        E.Name(startup),
                        E.NextMain('true')
                    )
                )
            )
        )
        return self.device.action(top)