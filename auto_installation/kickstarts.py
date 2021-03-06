"""This module will represent kickstart files
"""
# pylint: disable=C0103, W0403

import os
import logging

from pykickstart.parser import Script
from pykickstart.constants import KS_SCRIPT_PRE, KS_SCRIPT_POST

from constants import KS_FILES_DIR, KS_FILES_AUTO_DIR, \
    HOSTS, POST_SCRIPT_01, POST_SCRIPT_02, PRE_SCRIPT_01, PRE_SCRIPT_02, TEST_LEVEL
from utils import get_machine_ksl_map, get_ks_machine_map

loger = logging.getLogger('bender')


class KickStartFiles(object):
    """"""

    def __init__(self):
        self._liveimg = None

    @property
    def liveimg(self):
        return self._liveimg

    @liveimg.setter
    def liveimg(self, val):
        self._liveimg = val

    def _generate_ks_script(self,
                            content,
                            error_on_fail=True,
                            interp=None,
                            logfile=None,
                            script_type=KS_SCRIPT_POST,
                            in_chroot=False,
                            lineno=None):
        sp = Script(content)

        sp.errorOnFail = error_on_fail

        if interp:
            sp.interp = interp

        if logfile:
            sp.logfile = logfile

        sp.type = script_type
        sp.inChroot = in_chroot

        if lineno:
            sp.lineno = lineno
        return sp

    def _convert_to_auto_ks(self):
        loger.info("remove all old files under {}".format(KS_FILES_AUTO_DIR))
        os.system("rm -f {}/*".format(KS_FILES_AUTO_DIR))

        ks_machine_map = get_ks_machine_map()

        for ks in ks_machine_map:

            bkr_name = ks_machine_map.get(ks)

            nic_name = HOSTS.get(bkr_name).get("nic").keys()[0].split('-')[-1]

            ks_ = os.path.join(KS_FILES_DIR, ks)
            ks_out = os.path.join(KS_FILES_AUTO_DIR, ks)

            new_live_img = "liveimg --url=" + self._liveimg

            os.system("sed '/liveimg --url=/ c\{}' {} > {}".format(
                new_live_img, ks_, ks_out))

            if 'atv_bonda' not in ks:
                post_script = self._generate_ks_script(
                    POST_SCRIPT_01.format(nic_name) + bkr_name,
                    error_on_fail=False)
            else:
                post_script = self._generate_ks_script(
                    POST_SCRIPT_02 + bkr_name, error_on_fail=False)

            pre_script = self._generate_ks_script(
                PRE_SCRIPT_01 + PRE_SCRIPT_02,
                script_type=KS_SCRIPT_PRE,
                error_on_fail=False)

            with open(ks_out, "a") as fp:
                fp.write(pre_script.__str__())
                fp.write(post_script.__str__())

    def get_job_queue(self):
        print "current test level is %x" % TEST_LEVEL
        self._convert_to_auto_ks()

        return get_machine_ksl_map()


if __name__ == '__main__':
    ks = KickStartFiles()
    ks.liveimg = "http://fakeimg.squashfs"
    print(ks.get_job_queue())
