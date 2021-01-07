#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding: utf8
#
# Copyright 2019-2021 Denis Meyer
#
# This file is part of raspi-surveillance
#

"""Uploads file to Senders. Files get deleted after all uploads are done."""

import os
import shutil
import logging
import threading
import time
import datetime
import contextlib
from pathlib import Path


class FileSyncer:

    INVALID_LOCAL_FOLDERS = [
        '',
        '/'
    ]

    def __init__(self, settings, sender_list=[]):
        """Initialization. Senders must all be active (successfully initialized and started).

        :param settings: The settings
        :param sender_list: The list of senders
        """
        self.settings = settings
        self.sender_list = sender_list

        self.local_folder = self.settings.get('local_sync_folder_name')

        self.whitelist_file_prefixes = self.settings.sync_whitelist_file_prefixes
        self.whitelist_file_suffixes = self.settings.sync_whitelist_file_suffixes
        self.whitelist_file_names = self.settings.sync_whitelist_file_names
        self.blacklist_folder_prefixes = self.settings.sync_blacklist_folder_prefixes
        self.blacklist_folder_suffixes = self.settings.sync_blacklist_folder_suffixes
        self.blacklist_folder_names = self.settings.sync_blacklist_folder_names

        self.initialized = False
        self.syncing = False

    def _assert_local_folder(self):
        """Asserts the local folder structure

        :return: True if everything is OK, False else
        """
        if self.local_folder in self.INVALID_LOCAL_FOLDERS:
            logging.error(
                '"{}" is not a valid folder'.format(self.local_folder))
            return False

        logging.debug('Asserting local folder "{}"'.format(self.local_folder))
        try:
            if not self.local_folder or not os.path.exists(self.local_folder):
                os.mkdir(self.local_folder)
                if not os.path.exists(self.local_folder):
                    logging.error(
                        '"{}" does not exist on the filesystem'.format(self.local_folder))
                    return False
            elif not os.path.isdir(self.local_folder):
                logging.error(
                    '"{}" is not a folder on the filesystem'.format(self.local_folder))
                return False
        except Exception as e:
            logging.error('Failed to assert folder "{}": "{}"'.format(
                self.local_folder, e))
            return False

        return True

    def cleanup(self):
        pass

    def init(self):
        """Initialization, checks

        :return: True if successfully initialized, False else
        """
        logging.debug('Initializing')

        self.initialized = False

        logging.info('Local directory: "{}"'.format(self.local_folder))
        if not self._assert_local_folder():
            logging.error('Local folder could not be asserted')
            return False

        self.initialized = True

        return self.initialized

    def _cb_sync_done(self):
        """Callback on sync done"""
        self.syncing = False

    def sync(self, cleanup=False):
        """Synchronization logic.
        Iterates over files and directories under local file directory and uploads all found files. 
        Skips some temporary files and directories.

        :param cleanup: Boolean flag whether to clean up the local directory
        """
        if not self.initialized:
            logging.error('Not initialized')
            return

        if self.syncing:
            logging.info('Sync already in progress')
            return

        if not self.sender_list:
            logging.info('No active senders found. Skipping upload...')
            return

        logging.info('Syncing')
        self.syncing = True

        s_thread = ImageSyncThread(self.settings,
                                   self.sender_list,
                                   local_folder=self.local_folder,
                                   whitelist_file_prefixes=self.whitelist_file_prefixes,
                                   whitelist_file_suffixes=self.whitelist_file_suffixes,
                                   whitelist_file_names=self.whitelist_file_names,
                                   blacklist_folder_prefixes=self.blacklist_folder_prefixes,
                                   blacklist_folder_suffixes=self.blacklist_folder_suffixes,
                                   blacklist_folder_names=self.blacklist_folder_names,
                                   cb_sync_done=self._cb_sync_done,
                                   cleanup=cleanup)
        s_thread.start()


class ImageSyncThread(threading.Thread):

    def __init__(self,
                 settings,
                 sender_list,
                 local_folder,
                 whitelist_file_prefixes=[],
                 whitelist_file_suffixes=[],
                 whitelist_file_names=[],
                 blacklist_folder_prefixes=[],
                 blacklist_folder_suffixes=[],
                 blacklist_folder_names=[],
                 cb_sync_done=None,
                 cleanup=False):
        """Initializes the thread

        :param settings: The settings
        :param sender_list: The sender list
        :param local_folder: The local folder
        :param whitelist_file_prefixes: 
        :param whitelist_file_suffixes: 
        :param whitelist_file_names: 
        :param blacklist_folder_prefixes: 
        :param blacklist_folder_suffixes: 
        :param blacklist_folder_names: 
        :param cb_sync_done: Callback on sync done
        :param cleanup: Whether to clean up the local folder
        """
        threading.Thread.__init__(self)

        self.settings = settings
        self.sender_list = sender_list
        self.local_folder = local_folder
        self.whitelist_file_prefixes = whitelist_file_prefixes
        self.whitelist_file_suffixes = whitelist_file_suffixes
        self.whitelist_file_names = whitelist_file_names
        self.blacklist_folder_prefixes = blacklist_folder_prefixes
        self.blacklist_folder_suffixes = blacklist_folder_suffixes
        self.blacklist_folder_names = blacklist_folder_names
        self.cb_sync_done = cb_sync_done
        self.cleanup = cleanup

    @contextlib.contextmanager
    def _stopwatch(self, name):
        """Context manager to print how long a block of code took

        :param name: The name of the watched process
        """
        t0 = time.time()
        try:
            yield
        finally:
            t1 = time.time()
            logging.info(
                'Total elapsed time for "{}": {}'.format(name, t1 - t0))

    def _process(self, fname, prefixes, suffixes, names, whitelist=False):
        """Checks the given file or folder

        :fname: The file name
        :prefixes: The file name (whitelist)
        :suffixes: The file name (whitelist)
        :names: The file name (whitelist)
        :return: Process status
        """
        logging.debug('Processing fname="{}"'.format(fname))

        for prefix in prefixes:
            if fname.lower().startswith(prefix.lower()):
                return whitelist
        for suffix in suffixes:
            if fname.lower().endswith(suffix.lower()):
                return whitelist
        if fname in names:
            return whitelist

        return not whitelist

    def _process_file(self, fname):
        """Checks the given file

        :fname: The file name
        :return: Process status
        """
        logging.debug('Processing file')

        return self._process(
            fname,
            self.whitelist_file_prefixes,
            self.whitelist_file_suffixes,
            self.whitelist_file_names,
            whitelist=True)

    def _process_folder(self, fname):
        """Checks the given folder

        :fname: The folder name
        :return: Process status
        """
        logging.debug('Processing folder')

        return self._process(
            fname,
            self.blacklist_folder_prefixes,
            self.blacklist_folder_suffixes,
            self.blacklist_folder_names,
            whitelist=False)

    def _delete(self, fname):
        """Deletes a file or full folder

        :param fname: File or folder name
        """
        logging.debug('Delete [fname="{}"]'.format(fname))

        if os.path.exists(fname):
            if not os.path.isdir(fname):
                logging.debug('Removing file "{}"'.format(fname))
                os.remove(fname)
            else:
                logging.debug('Removing folder "{}"'.format(fname))
                shutil.rmtree(fname)
        else:
            logging.debug('Path does not exist "{}"'.format(fname))

    def _clean_folder(self, folder, file_ignore_list=[]):
        """Cleans a full folder

        :param folder: Folder name
        :param file_ignore_list: File ignore list
        """
        logging.debug('Deleting [folder="{}", ignoring="{}"]'.format(
            folder, file_ignore_list))

        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                path_ignore_list = []
                for p in file_ignore_list:
                    _path = Path(p).parent.as_posix()
                    while '//' in _path:
                        _path = _path.replace('//', '/')
                    path_ignore_list.append(_path)
                folder_path = Path(folder).as_posix()
                while '//' in folder_path:
                    folder_path = folder_path.replace('//', '/')
                if folder_path in path_ignore_list:
                    logging.debug('Skipping "{}"'.format(file_path))
                else:
                    logging.debug('Deleting "{}"'.format(file_path))
                    self._delete(file_path)
            except Exception as e:
                logging.error('Error deleting "{}"'.format(e))

    def run(self):
        """Runs the thread"""
        if self.cleanup:
            logging.info('Starting file sync thread in cleanup mode')
            try:
                self._clean_folder(self.local_folder)
            finally:
                logging.info('Done cleanup')
                if self.cb_sync_done:
                    self.cb_sync_done()
        else:
            logging.info('Starting file sync thread')

            try:
                # Store failed files for every Sender
                failed_files = {}
                # Store files that have been successfully uploaded at least by one sender
                uploaded_at_least_once = []
                curr_datetime = '{:%Y-%m-%d-%H-%M-%S}'.format(
                    datetime.datetime.now())
                for dn, dirs, files in os.walk(self.local_folder):
                    subfolder = dn[len(self.local_folder):].strip(os.path.sep)
                    logging.debug('Descending into "{}"...'.format(
                        subfolder if subfolder else '/'))

                    # Files of the (sub-)directory
                    for name in files:
                        fullname = os.path.join(dn, name)
                        if not self._process_file(name):
                            logging.debug(
                                'Deleting file "{}" without upload'.format(name))
                            self._delete(fullname)
                        else:
                            with self._stopwatch('Upload image to Senders'):
                                subfolder_drpbx = os.path.join(
                                    subfolder, curr_datetime)
                                logging.debug('Uploading [fullname="{}", subfolder="{}", name="{}"]'
                                              .format(fullname, subfolder_drpbx, name))
                                for sender in self.sender_list:
                                    func = sender.send_video if fullname.endswith(
                                        '.mp4') else sender.send_image
                                    if not func(fullname, subfolder_drpbx, name):
                                        logging.warn('Failed to send "{}" to Sender "{}"'
                                                     .format(fullname, sender.get_name()))
                                        if not sender.get_name() in failed_files:
                                            failed_files[sender.get_name()] = [
                                            ]
                                        failed_files[sender.get_name()].append(
                                            fullname)
                                    else:
                                        logging.debug('Successfully uploaded "{}" to Sender "{}"'
                                                      .format(fullname, sender.get_name()))
                                        if not fullname in uploaded_at_least_once:
                                            uploaded_at_least_once.append(
                                                fullname)

                    # Subdirectories of the (sub-)directory
                    keep = []
                    for name in dirs:
                        if not self._process_folder(name):
                            logging.debug('Skipping folder "{}"'.format(name))
                        else:
                            logging.debug('Keeping folder {}'.format(name))
                            keep.append(name)
                    dirs[:] = keep

                # Log files that have not been successfully uploaded, per sender
                if failed_files:
                    logging.info('Files failed to upload:')
                    for key, value in failed_files.items():
                        logging.info('\t- Sender "{}"'.format(key))
                        for v in value:
                            logging.info('\t\t- "{}"'.format(v))

                # Sleep for a certain amount of time to avoid deletion conflicts
                time.sleep(self.settings.get('sleep')['sync_done_sec'])

                # Delete files that have been successfully uploaded at least by one sender
                if uploaded_at_least_once:
                    logging.info(
                        'Deleting files that have been uploaded at least by one Sender')
                    for fname in uploaded_at_least_once:
                        self._delete(fname)
            finally:
                logging.info('Done syncing')
                if self.cb_sync_done:
                    self.cb_sync_done()
