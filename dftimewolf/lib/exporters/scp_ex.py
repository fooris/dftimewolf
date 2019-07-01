# -*- coding: utf-8 -*-
"""Send files using scp."""

from __future__ import unicode_literals

import subprocess

from dftimewolf.lib.module import BaseModule

class Scp(BaseModule):
  """Copies the files in the previous module's output to a given path.

  input: List of paths to copy the files from.
  output: The directory in which the files have been copied.

  Attributes:
    _paths (list[str]): List of files to copy.
    _user (str): Username at destination host.
    _hostname (str): Hostname of destination.
    _destination (str): Path to destination on host.
    _id_file (str): Identity file to use.
  """

  def __init__(self, state):
    super(Scp, self).__init__(state)
    self._paths = None
    self._user = None
    self._hostname = None
    self._destination = None
    self._id_file = None

  def setup(self, # pylint: disable=arguments-differ
            paths, destination, user, hostname, id_file):
    """Sets up the _target_directory attribute.

    Args:
      paths (list[str]): List of files to copy.
      user (str): Username at destination host.
      hostname (str): Hostname of destination.
      destination (str): Path to destination on host.
      id_file (str): Identity file to use.
    """
    self._destination = destination
    self._hostname = hostname
    self._id_file = id_file
    self._paths = paths.split(",")
    self._user = user

    if not self._ssh_available():
      self.state.add_error("Unable to connect to host.", critical=True)

  def cleanup(self):
    pass

  def process(self):
    """Copies the list of paths to the destination on user@hostname"""
    dest = self._destination
    if self._hostname:
      dest = "{0:s}@{1:s}:{2:s}".format(self._user, self._hostname,
                                        self._destination)
    cmd = ["scp"]
    cmd.extend(self._paths)
    cmd.append(dest)
    ret = subprocess.call(cmd)
    if ret:
      self.state.add_error("Failed copying {0:s}".format(self._paths),
                           critical=False)

  def _ssh_available(self):
    """Checks that the SSH authentication succeeds on a given host.

    Returns:
      True if host can be reached, false otherwise.
    """
    if not self._hostname:
      return True
    command = ["ssh", "-q", "-l", self._user, self._hostname, "true"]
    if self._id_file:
      command.extend(["-i", self._id_file])
    ret = subprocess.call(command)
    return not ret
