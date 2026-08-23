"""Windows compatibility shim for genlayer-test 0.29.2 direct mode.

The runner replaces fd 0 with a temporary file and unlinks it while fd 0 is
still open. Windows rejects that unlink. Keep the file until VM teardown,
after stdin has been restored; contract behavior is unchanged.
"""

import os
import tempfile

from gltest.direct import loader
from gltest.direct.vm import VMContext


def _inject_message_windows_safe(vm):
    from genlayer.py import calldata
    from genlayer.py.types import Address

    sender = Address(vm.sender) if isinstance(vm.sender, bytes) else vm.sender
    contract = Address(vm._contract_address) if isinstance(vm._contract_address, bytes) else vm._contract_address
    origin = Address(vm.origin) if isinstance(vm.origin, bytes) else vm.origin
    message = {
        "contract_address": contract,
        "sender_address": sender,
        "origin_address": origin,
        "stack": [],
        "value": vm._value,
        "datetime": vm._datetime,
        "is_init": False,
        "chain_id": vm._chain_id,
        "entry_kind": 0,
        "entry_data": b"",
        "entry_stage_data": None,
    }
    fd, path = tempfile.mkstemp()
    os.write(fd, calldata.encode(message))
    os.lseek(fd, 0, os.SEEK_SET)
    vm._original_stdin_fd = os.dup(0)
    os.dup2(fd, 0)
    os.close(fd)
    vm._chronicle_stdin_path = path


_original_cleanup = VMContext._cleanup_after_deactivate


def _cleanup_with_tempfile(self):
    path = getattr(self, "_chronicle_stdin_path", None)
    _original_cleanup(self)
    if path:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        self._chronicle_stdin_path = None


loader._inject_message_to_fd0 = _inject_message_windows_safe
VMContext._cleanup_after_deactivate = _cleanup_with_tempfile
